from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from datetime import datetime
import bcrypt
import smtplib
from email.mime.text import MIMEText
from random import randint
import os

app = Flask(__name__, static_folder='')

client = MongoClient('mongodb+srv://leocelestine:Bethelboyy@ktcluster.9gvhl6k.mongodb.net/?retryWrites=true&w=majority')
db = client.ktapp_db

users_collection = db.users
attendance_collection = db.attendance
otps_collection = db.otps

def send_email(to, subject, body):
    sender = 'leocelestine.s@gmail.com'
    password = 'wyxq kvwx qzsh mqee'  # Replace with the app password
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [to], msg.as_string())
            print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory('', 'admin.html')

@app.route('/staff')
def serve_staff():
    return send_from_directory('', 'staff.html')

@app.route('/request-reset', methods=['POST'])
def request_reset():
    data = request.get_json()
    username = data['username']
    email = 'leocelestine.s@gmail.com'

    otp = str(randint(100000, 999999))
    created_at = datetime.now().isoformat()

    otps_collection.delete_many({'username': username})
    otps_collection.insert_one({'username': username, 'otp': otp, 'created_at': created_at})

    send_email(email, 'Your OTP Code', f'Your OTP code is {otp}')

    return jsonify({'message': 'OTP sent'})

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data['username']
    otp = data['otp']
    new_password = data['new_password']

    record = otps_collection.find_one({'username': username, 'otp': otp})

    if not record:
        return jsonify({'message': 'Invalid OTP'}), 401

    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    users_collection.update_one({'username': username}, {'$set': {'password': hashed_password}})
    otps_collection.delete_many({'username': username})

    return jsonify({'message': 'Password reset successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = users_collection.find_one({'username': username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    employee = data['employee']
    date = data['date']
    time = data['time']
    type = data['type']

    attendance_collection.insert_one({
        'employee': employee,
        'date': date,
        'time': time,
        'type': type
    })

    return jsonify({'message': f'Time {type} marked successfully'})

@app.route('/get-attendance', methods=['GET'])
def get_attendance():
    records = attendance_collection.find()
    attendance_data = {}

    for record in records:
        employee = record['employee']
        date = record['date']
        time = record['time']
        type = record['type']

        if employee not in attendance_data:
            attendance_data[employee] = {}

        year, month, day = date.split('-')
        if year not in attendance_data[employee]:
            attendance_data[employee][year] = {}
        if month not in attendance_data[employee][year]:
            attendance_data[employee][year][month] = {}
        if day not in attendance_data[employee][year][month]:
            attendance_data[employee][year][month][day] = []

        attendance_data[employee][year][month][day].append({'time': time, 'type': type})

    return jsonify(attendance_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
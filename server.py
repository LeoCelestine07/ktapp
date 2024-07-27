from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import bcrypt
import smtplib
from email.mime.text import MIMEText
from random import randint
import logging

app = Flask(__name__, static_folder='.')
logging.basicConfig(level=logging.INFO)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT,
            date TEXT,
            time TEXT,
            type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            otp TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def send_email(to, subject, body):
    try:
        sender = 'leocelestine.s@gmail.com'
        password = 'wyxq kvwx qzsh mqee'  # Replace with the app password
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [to], msg.as_string())
            logging.info(f"Email sent to {to}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

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
    try:
        data = request.get_json()
        username = data['username']
        email = 'leocelestine.s@gmail.com'  # Email to send OTP to

        otp = str(randint(100000, 999999))
        created_at = datetime.now().isoformat()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM otps WHERE username = ?', (username,))
        cursor.execute('''
            INSERT INTO otps (username, otp, created_at)
            VALUES (?, ?, ?)
        ''', (username, otp, created_at))
        conn.commit()
        conn.close()

        send_email(email, 'Your OTP Code', f'Your OTP code is {otp}')

        return jsonify({'message': 'OTP sent'})
    except Exception as e:
        logging.error(f"Error in request_reset: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        username = data['username']
        otp = data['otp']
        new_password = data['new_password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT otp FROM otps WHERE username = ? AND otp = ?', (username, otp))
        record = cursor.fetchone()

        if not record:
            conn.close()
            return jsonify({'message': 'Invalid OTP'}), 401

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))
        cursor.execute('DELETE FROM otps WHERE username = ?', (username,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Password reset successfully'})
    except Exception as e:
        logging.error(f"Error in reset_password: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        record = cursor.fetchone()
        conn.close()

        if record and bcrypt.checkpw(password.encode('utf-8'), record[0]):
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        logging.error(f"Error in login: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()
        employee = data['employee']
        date = data['date']
        time = data['time']
        type = data['type']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance (employee, date, time, type)
            VALUES (?, ?, ?, ?)
        ''', (employee, date, time, type))

        conn.commit()
        conn.close()

        return jsonify({'message': f'Time {type} marked successfully'})
    except Exception as e:
        logging.error(f"Error in mark_attendance: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/get-attendance', methods=['GET'])
def get_attendance():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM attendance ORDER BY employee, date')
        records = cursor.fetchall()
        conn.close()

        attendance_data = {}
        for record in records:
            employee = record[1]
            date = record[2]
            time = record[3]
            type = record[4]

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
    except Exception as e:
        logging.error(f"Error in get_attendance: {e}")
        return jsonify({'message': 'An error occurred'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
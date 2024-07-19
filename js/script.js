document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Login successful') {
                if (username === 'admin') {
                    window.location.href = '/admin';
                } else {
                    sessionStorage.setItem('username', username.charAt(0).toUpperCase() + username.slice(1));
                    window.location.href = '/staff';
                }
            } else {
                document.getElementById('status').innerText = 'Invalid credentials';
                clearMessageAfterDelay('status');
            }
        })
        .catch(error => {
            document.getElementById('status').innerText = 'Error: ' + error.message;
            clearMessageAfterDelay('status');
        });
});

document.getElementById('resetPassword').addEventListener('click', function () {
    document.getElementById('resetForm').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
});

document.getElementById('otpForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('otpUsername').value;

    fetch('/request-reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('otpStatus').innerText = data.message;
            clearMessageAfterDelay('otpStatus');
            if (data.message === 'OTP sent') {
                document.getElementById('newPasswordForm').style.display = 'block';
                document.getElementById('otpForm').style.display = 'none';
            }
        })
        .catch(error => {
            document.getElementById('otpStatus').innerText = 'Error: ' + error.message;
            clearMessageAfterDelay('otpStatus');
        });
});

document.getElementById('newPasswordForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('otpUsername').value;
    const otp = document.getElementById('otp').value;
    const newPassword = document.getElementById('newPassword').value;

    fetch('/reset-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, otp, new_password: newPassword })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('newPasswordStatus').innerText = data.message;
            clearMessageAfterDelay('newPasswordStatus');
            if (data.message === 'Password reset successfully') {
                document.getElementById('resetForm').style.display = 'none';
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('status').innerText = 'Password reset successfully';
                clearMessageAfterDelay('status');
            }
        })
        .catch(error => {
            document.getElementById('newPasswordStatus').innerText = 'Error: ' + error.message;
            clearMessageAfterDelay('newPasswordStatus');
        });
});

function clearMessageAfterDelay(elementId) {
    setTimeout(function () {
        document.getElementById(elementId).innerText = '';
    }, 5000);
}
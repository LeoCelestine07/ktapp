document.getElementById('markTimeIn').addEventListener('click', function (e) {
    e.preventDefault();
    checkLocation('in');
});

document.getElementById('markTimeOut').addEventListener('click', function (e) {
    e.preventDefault();
    checkLocation('out');
});

function checkLocation(type) {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const officeLat = 12.931138;
            const officeLon = 80.179043;
            const distance = calculateDistance(lat, lon, officeLat, officeLon);

            if (distance <= 1) {
                markAttendance(type);
            } else {
                displayMessage('You are not in the office location');
            }
        }, function (error) {
            displayMessage('Error in getting location: ' + error.message);
        });
    } else {
        displayMessage('Geolocation is not available');
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
        0.5 - Math.cos(dLat) / 2 +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        (1 - Math.cos(dLon)) / 2;

    return R * 2 * Math.asin(Math.sqrt(a));
}

function markAttendance(type) {
    const employeeName = sessionStorage.getItem('username');
    const currentDate = new Date().toISOString().split('T')[0];
    const currentTime = new Date().toLocaleTimeString('en-GB', { hour12: false });

    fetch('/mark-attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            employee: employeeName,
            date: currentDate,
            time: currentTime,
            type: type
        })
    })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.message);
        })
        .catch(error => {
            displayMessage('Error: ' + error.message);
        });
}

function displayMessage(message) {
    const statusElement = document.getElementById('status');
    statusElement.innerText = message;
    setTimeout(function () {
        statusElement.innerText = '';
    }, 5000);
}
document.addEventListener('DOMContentLoaded', function () {
    fetch('/get-attendance')
        .then(response => response.json())
        .then(data => {
            let attendanceData = '';
            const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

            for (let employee in data) {
                attendanceData += `<div class="employee"><h2 class="employee-name">${employee.charAt(0).toUpperCase() + employee.slice(1)}</h2><div class="years" style="display: none;">`;

                for (let year in data[employee]) {
                    attendanceData += `<h3 class="year">${year}</h3><div class="months" style="display: none;">`;

                    for (let month in data[employee][year]) {
                        attendanceData += `<div class="month"><h4 class="month-name">${months[parseInt(month) - 1]}</h4><div class="days" style="display: none;">`;

                        for (let day in data[employee][year][month]) {
                            const formattedDate = `${day}/${parseInt(month) + 1}/${year}`;
                            attendanceData += `<div class="day"><h5 class="day-name">${formattedDate}</h5><div class="times" style="display: none;">`;

                            let timeInOutPairs = data[employee][year][month][day].reduce((acc, record) => {
                                if (record.type === 'in') {
                                    acc.push({ timeIn: record.time, timeOut: null });
                                } else {
                                    if (acc.length > 0 && acc[acc.length - 1].timeOut === null) {
                                        acc[acc.length - 1].timeOut = record.time;
                                    } else {
                                        acc.push({ timeIn: null, timeOut: record.time });
                                    }
                                }
                                return acc;
                            }, []);

                            timeInOutPairs.forEach((pair, index) => {
                                attendanceData += `<p>${index + 1}. Time In: ${pair.timeIn || 'N/A'}, Time Out: ${pair.timeOut || 'N/A'}</p>`;
                            });

                            attendanceData += `</div></div>`;
                        }

                        attendanceData += `</div></div>`;
                    }

                    attendanceData += `</div>`;
                }

                attendanceData += `</div></div>`;
            }

            document.getElementById('attendanceData').innerHTML = attendanceData;

            document.querySelectorAll('.employee-name').forEach(element => {
                element.addEventListener('click', function () {
                    const yearsDiv = this.nextElementSibling;
                    if (yearsDiv.style.display === 'none') {
                        resetNestedDivs(yearsDiv);
                    }
                    yearsDiv.style.display = yearsDiv.style.display === 'none' ? 'block' : 'none';
                });
            });

            document.querySelectorAll('.year').forEach(element => {
                element.addEventListener('click', function () {
                    const monthsDiv = this.nextElementSibling;
                    monthsDiv.style.display = monthsDiv.style.display === 'none' ? 'block' : 'none';
                });
            });

            document.querySelectorAll('.month-name').forEach(element => {
                element.addEventListener('click', function () {
                    const daysDiv = this.nextElementSibling;
                    daysDiv.style.display = daysDiv.style.display === 'none' ? 'block' : 'none';
                });
            });

            document.querySelectorAll('.day-name').forEach(element => {
                element.addEventListener('click', function () {
                    const timesDiv = this.nextElementSibling;
                    timesDiv.style.display = timesDiv.style.display === 'none' ? 'block' : 'none';
                });
            });

            function resetNestedDivs(parentDiv) {
                parentDiv.querySelectorAll('.months, .days, .times').forEach(div => {
                    div.style.display = 'none';
                });
            }
        });
});
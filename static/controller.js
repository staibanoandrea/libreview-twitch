const maxData = 60;
var postId = 1;

function loopData() {
    var value = document.getElementById("value");
    var trendArrow = document.getElementById("trend-arrow");
    var container = document.getElementById("container")

    var ctx_live = document.getElementById("myChart");
    var myChart = createChart(ctx_live);

    var update = function () {
        $.ajax({
            type: "GET",
            url: "http://127.0.0.1:1337/latestglucose",
            dataType: "json",
            success: function (response) {
                animatedUpdateValue(value, response['Value']);
                container.style.backgroundColor = response['MeasurementColor'];
                trendArrow.style.transform = "rotate(" + response['TrendArrow'] + "deg)";
                updateGraph(myChart, response);
            }
        });
    }

    update();
    setInterval(update, 60000);
}

function createChart(ctx_live) {
    return new Chart(ctx_live, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderWidth: 1.5,
                borderColor: '#000000',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
                line: {
                    tension: 0.4
                }
            },
            scales: {
                x: {
                    ticks: {
                        display: false
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                },
                y: {
                    type: 'linear',
                    grace: '5%',
                    ticks: {
                        display: true,
                        color: '#000000',
                        font: {
                            size: 8,
                            family: 'Inter'
                        }
                    },
                    grid: {
                        display: true,
                        color: '#000000',
                        drawBorder: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function updateGraph(chart, response) {
    if (getDatasetLength(chart) == 0) {
        for (const value of response['DataHistory']) {
            chart.data.labels.push(postId++);
            chart.data.datasets[0].data.push(value);
        }
    } else {
        chart.data.labels.push(postId++);
        chart.data.datasets[0].data.push(response['Value']);
    }
    while (getDatasetLength(chart) > maxData) {
        chart.data.labels.splice(0, 1);
        chart.data.datasets[0].data.splice(0, 1);
    }
    chart.update();
}

function getDatasetLength(chart) {
    if (chart == null) return 0;
    return chart.data.datasets[0].data.length;
}

function animatedUpdateValue(value, newValue) {
    const $value = $('#value');
    $({
        counter: Number(value.innerHTML) // Starting value, which is the last known count value.
    }).animate({
        counter: Number(newValue) // Value to animate to, which is the new count value.
    }, {
        duration: 1000,
        easing: 'swing',
        step: function () {
            $value.text(Math.round(this.counter));
        },
        complete: function () {
            value = newValue; // Update the count value after the animation to compare it later again.
        }
    });
}
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
                borderWidth: 1,
                borderColor: '#000'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
                point: {
                    radius: 0
                },
                line: {
                    tension: 0.5
                }
            },
            scales: {
                x: {
                    ticks: {
                        display: false
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    grace: 0,
                    ticks: {
                        display: true,
                        color: '#000',
                        font: {
                            size: 10
                        }
                    },
                    grid: {
                        display: true
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/*const maxData = 60;
var postId = 1;
var myChart;
function getGraph() {
    var ctx_live = document.getElementById("myChart");
    myChart = new Chart(ctx_live, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderWidth: 1,
                borderColor: '#000'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
                point: {
                    radius: 0
                },
                line: {
                    tension: 0.5
                }
            },
            scales: {
                x: {
                    ticks: {
                        display: false
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    grace: 0,
                    ticks: {
                        display: true,
                        color: '#000',
                        font: {
                            size: 10
                        }
                    },
                    grid: {
                        display: true
                    }
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });*/

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

/*var updateGraph = function () {
    $.ajax({
        type: "GET",
        url: "http://127.0.0.1:1337/latestglucose",
        dataType: "json",
        success: function (response) {
            if (getDatasetLength() == 0) {
                for (const value of response['DataHistory']) {
                    myChart.data.labels.push(postId++);
                    myChart.data.datasets[0].data.push(value);
                }
            } else {
                myChart.data.labels.push(postId++);
                myChart.data.datasets[0].data.push(response['Value']);
            }
            while (getDatasetLength() > maxData) {
                myChart.data.labels.splice(0, 1);
                myChart.data.datasets[0].data.splice(0, 1);
            }
            myChart.update();
        }
    });
}

updateGraph();
setInterval(updateGraph, 60000);
}*/

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
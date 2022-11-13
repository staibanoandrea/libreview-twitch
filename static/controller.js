function getData() {
    var value = document.getElementById("value");
    var trendArrow = document.getElementById("trend-arrow");
    var timestamp = document.getElementById("timestamp");
    var container = document.getElementById("container")

    $.ajax({
        type: "GET",
        url: "http://127.0.0.1:1337/latestglucose",
        dataType: "json",
        success: function (response) {
            value.innerHTML = response['Value'];
            /*trendArrow.innerHTML = response['TrendArrow'];*/
            timestamp.innerHTML = response['Timestamp'].substring(17, 25) + " CET";
            container.style.backgroundColor = response['MeasurementColor'];
            trendArrow.style.transform = "rotate(" + response['TrendArrow'] + "deg)";
        }
    });
}
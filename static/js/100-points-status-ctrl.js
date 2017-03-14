// Project: VSTS Discovery extension
// JavaScript functions for controlling 100 points status component
// Author: Yichen Lu
// Create Date: 01-Feb-2017
// Update Date: 20-Feb-2017

function randomColors() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgba(" + r + "," + g + "," + b + ", 0.4)";
}

function randomColorSet(labels) {
    var colorSet = [];
    for (var i = labels.length - 1; i >= 0; i--) {
        colorSet.push(randomColors());
    }
    return colorSet;
}

var colorSet;
// pie chart
function getWeeklyDistribution(date) {
    $.ajax({
        url: 'http://127.0.0.1:8000/points/distribution/'+date,
        type: 'GET',
        dataType: 'json',
    })
    .done(function(data) {
        console.log("success");
        var chartLabels = [];
        var labelVal = [];
        // read data
        var content = data.given_points;
        $.each(content, function(index, obj) {
            $.each(obj, function(key, val) {
                if (key == "to_member") {
                    chartLabels.push(val);
                }
                if (key == "points") {
                    labelVal.push(val);
                }
            });
        });

        // set up pie chart
        var ctx = $("#myChart");
        if (colorSet===undefined) {
            colorSet = randomColorSet(chartLabels);
        }
        var pieDataConf = {
            labels: chartLabels,
            datasets: [
                {
                    data: labelVal,
                    backgroundColor: colorSet,
                    hoverBackgroundColor: colorSet
                }]
        };

        var myPieChart = new Chart(ctx,{
            type: 'pie',
            data: pieDataConf,
            options: {
                responsive: false
            }
        });

    })
    .fail(function() {
        console.log("error");
    })
    .always(function() {
        console.log("complete");
    });

}

// function getHistoryDistribution(startDate, endDate) {
//     $.ajax({
//         url: 'http://127.0.0.1:8000/points/distribution/history',
//         type: 'GET',
//         dataType: 'json',
//     })
//     .done(function(data) {
//         console.log("success");
//         var chartLabels = [];
//         var labelVal = [];
//         // read data
//         $.each(data, function(index, val) {
//             if (index == "week") {
//                 chartLabels.push()
//             }
//             $.each(array/object, function(index, val) {
//                  /* iterate through array or object */
//             });
//         });
//     })
//     .fail(function() {
//         console.log("error");
//     })
//     .always(function() {
//         console.log("complete");
//     });
// }

function load100PtStatus() {
    $('#100-points-components').load("components/100-points-status.html", function(response, status, xhr){
        if (status == "success") {
            console.log("start ajax");
            var now = moment().format("YYYY-MM-DD");
            getWeeklyDistribution(now);
        }
    });
}




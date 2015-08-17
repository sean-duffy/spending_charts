$(function () {
    $('#barchart1').highcharts({
        chart: {
            type: 'column'
        },

        tooltip: false,

        credits: false,

        title: {
            text: 'Spending by Week'
        },

        xAxis: {
            type: 'category'
        },

        yAxis: {
            title: {
                text: 'Total Spend'
            },
            type: 'logarithmic'

        },

        legend: {
            enabled: false
        },

        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    format: '£{point.y:2.2f}',
                    padding: 2,
                }
            }
        },

        series: [{
            name: "Weeks",
            colorByPoint: true,
            data: [
                {datapoints}
            ]
        }],

    });
});

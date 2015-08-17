$(function () {
    $('#chart{chart_number}').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },

        credits: false,

        title: {
               text: '{week_name} <br/> Total: £{week_total}'
        },

        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>',
            hideDelay: 100
        },

        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: false
                }
        },

        series: [{
            name: "Percentage",
            colorByPoint: true,
            data: [
                {datapoints}
            ]
        }]
    });
});

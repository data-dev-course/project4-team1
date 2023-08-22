
Highcharts.chart('recent_ratio_pie_chart', {
    chart: {
        plotBackgroundColor: null,
        plotBorderWidth: 0,
        plotShadow: false
    },
    title: {
        text: '',
        align: 'center',
        verticalAlign: 'middle',
        y: 60
    },
    tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
    },
    accessibility: {
        point: {
            valueSuffix: '%'
        }
    },
    plotOptions: {
        pie: {
            dataLabels: {
                enabled: true,
                distance: -30,
                format:'{point.percentage:.1f}%',
                style: {
                    fontWeight: 'bold',
                    color: 'white'
                }
            },
            startAngle: -90,
            endAngle: 90,
            center: ['50%', '75%'],
            size: '150%'
        }
    },
    series: [{
        type: 'pie',
        name: '비율',
        innerSize: '50%',
        colors: [
            '#B137A3', '#43ABAF',
        ],
        data: [
            ['상주', 73.86],
            ['비상주', 26.14],
            // {
            //     name: 'Other',
            //     y: 3.77,
            //     dataLabels: {
            //         enabled: false
            //     }
            // }
        ]
    }]
});



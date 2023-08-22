
Highcharts.chart('age_ratio_pie_chart', {
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
            '#FFE45C', '#FD7B49','#E8395C','#B137A3','#6957CB','#43ABAF'
        ],
        data: [
            ['10대이상', 16.00],
            ['20대', 16.00],
            ['30대', 16.00],
            ['40대', 16.00],
            ['50대', 16.00],
            ['60대이상', 16.00],
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



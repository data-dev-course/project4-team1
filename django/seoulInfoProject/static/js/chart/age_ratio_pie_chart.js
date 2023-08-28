var get_json = JSON.parse(
    document.getElementById('congest').textContent
);
var congest = JSON.parse(get_json)[0]['fields']

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
            ['10대이상', congest['ppltn_rate_0'] + congest['ppltn_rate_10']],
            ['20대', congest['ppltn_rate_20']],
            ['30대', congest['ppltn_rate_30']],
            ['40대', congest['ppltn_rate_40']],
            ['50대', congest['ppltn_rate_50']],
            ['60대이상', congest['ppltn_rate_60']+congest['ppltn_rate_70']],

        ]
    }]
});



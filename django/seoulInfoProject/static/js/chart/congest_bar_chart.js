// var congest = JSON.parse("{{q_set|escapejs }}");
// var placeData = JSON.parse(document.getElementById('jsonData').textContent);
// var test = JSON.parse(document.getElementById('jsonData').textContent);
// const data =document.currentScript.dataset;
// const test = data.q_set;
var congest_fcst_json = JSON.parse(
    document.getElementById('congest_fcst').textContent
);
var congest_past_json = JSON.parse(
    document.getElementById('congest_past').textContent
);

var congest_fcst = JSON.parse(congest_fcst_json)
var congest_past = JSON.parse(congest_past_json)

console.log(congest_fcst)
console.log(congest_past)

var color_list =[]
var data_list = []

for (num in congest_past){
    console.log(congest_past[num]['fields'])
    past_data = congest_past[num]['fields']
    if (past_data['area_congest_lvl'] == '여유'){
        color_list.push("#00d369")
    } else if (past_data['area_congest_lvl'] == '보통'){
        color_list.push("#ffb100")
    } else if (past_data['area_congest_lvl'] == '약간 붐빔'){
        color_list.push("#ff8040")
    } else if (past_data['area_congest_lvl'] == '붐빔'){
        color_list.push("#dd1f3d")
    }

    data_list.push([
        past_data['timestamp'],
        past_data['area_ppltn_max']
    ])
}

for (num in congest_fcst){
    fcst_data = congest_fcst[num]['fields']
    if (fcst_data['fcst_congest_lvl'] == '여유'){
        color_list.push("#00d369")
    } else if (fcst_data['fcst_congest_lvl'] == '보통'){
        color_list.push("#ffb100")
    } else if (fcst_data['fcst_congest_lvl'] == '약간 붐빔'){
        color_list.push("#ff8040")
    } else if (fcst_data['fcst_congest_lvl'] == '붐빔'){
        color_list.push("#dd1f3d")
    }

    data_list.push([
        fcst_data['fcst_time'],
        fcst_data['fcst_ppltn_max']
    ])
}

console.log(color_list)
console.log(data_list)

document.addEventListener("DOMContentLoaded", function() {
    var el = document.getElementById('gender_ratio_pie_chart');
    var congest = JSON.parse(el.getAttribute("list_data"));
    console.log(congest);
});

Highcharts.chart('congest_bar_chart', {
    chart: {
        type: 'column'
    },
    title: {
        text: 'World\'s largest cities per 2021'
    },
    // subtitle: {
    //     text: 'Source: <a href="https://worldpopulationreview.com/world-cities" target="_blank">World Population Review</a>'
    // },
    xAxis: {
        type: 'category',
        labels: {
            autoRotation: [-45, -90],
            style: {
                fontSize: '13px',
                fontFamily: 'Verdana, sans-serif',
                step: '2',
            }
        }
    },
    yAxis: {
        min: 0,
        title: {
            text: 'Population (millions)'
        }
    },
    legend: {
        enabled: false
    },
    tooltip: {
        pointFormat: 'Population in 2021: <b>{point.y:.1f} millions</b>'
    },
    series: [{
        name: 'Population',
        colors: color_list,
        colorByPoint: true,
        groupPadding: 0,
        data: data_list
        ,
        dataLabels: {
            enabled: true,
            rotation: -90,
            color: '#FFFFFF',
            align: 'right',
            //format: '{point.y:}', // one decimal
            y: 10, // 10 pixels down from the top
            style: {
                fontSize: '13px',
                fontFamily: 'Verdana, sans-serif'
            }
        }
    }]
});

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

var color_list =[]
var data_list = []
var category_list = []

for (num in congest_past){
    var past_data = congest_past[num]['fields']
    var date = new Date(past_data['timestamp'])

    if (past_data['area_congest_lvl'] == '여유'){
        color = "#00d369"
    } else if (past_data['area_congest_lvl'] == '보통'){
        color = "#ffb100"
    } else if (past_data['area_congest_lvl'] == '약간 붐빔'){
        color = "#ff8040"
    } else if (past_data['area_congest_lvl'] == '붐빔'){
        color = "#dd1f3d"
    }
    color_list.push(color)
    int_num= parseInt(num)
    ppltn_max = parseInt(past_data['area_ppltn_max']).toLocaleString()
    ppltn_min = parseInt(past_data['area_ppltn_min']).toLocaleString()

    if (int_num === congest_past.length-1){
        time = '현재'
        past_congest_lvl = '혼잡도: '+ past_data['area_congest_lvl']
        ppltn_range = '인구수: '
    }else if(congest_past.length > 12 && int_num % 6 === 0){

        time = date.getHours()+'시'
        past_congest_lvl = '과거 혼잡도: '+ past_data['area_congest_lvl']
        ppltn_range = '과거 인구수: '
    }else if(int_num % Math.floor(congest_past.length / 2) === 0 ){
        time = date.getHours()+'시'
        past_congest_lvl = '과거 혼잡도: '+ past_data['area_congest_lvl']
        ppltn_range = '과거 인구수: '
    }
    else{
        time = ''
        past_congest_lvl = '과거 혼잡도: '+ past_data['area_congest_lvl']
        ppltn_range = '과거 인구수: '
    }

    category_list.push(time)
    data_list.push({
        'y': past_data['area_ppltn_max'],
        'custom': {
            'time' : date.getHours()+'시',
            'congest_lvl' : past_congest_lvl,
            'ppltn_range' : ppltn_range,
            'color' : color,
            'ppltn_max' : ppltn_max,
            'ppltn_min' : ppltn_min,
        }
    })
}

for (num in congest_fcst){
    fcst_data = congest_fcst[num]['fields']
    var date = new Date(fcst_data['fcst_time'])
    if (fcst_data['fcst_congest_lvl'] == '여유'){
        color = "#00d369"
    } else if (fcst_data['fcst_congest_lvl'] == '보통'){
        color = "#ffb100"
    } else if (fcst_data['fcst_congest_lvl'] == '약간 붐빔'){
        color = "#ff8040"
    } else if (fcst_data['fcst_congest_lvl'] == '붐빔'){
        color = "#dd1f3d"
    }
    color_list.push(color)
    ppltn_max = parseInt(fcst_data['fcst_ppltn_max']).toLocaleString()
    ppltn_min = parseInt(fcst_data['fcst_ppltn_min']).toLocaleString()


    if((parseInt(num)+1) % 6 === 0){
        time = date.getHours()+'시'
    }else{
        time = ''
    }
    category_list.push(time)
    data_list.push({
        'y':fcst_data['fcst_ppltn_max'],
        'custom' : {
            'time' : date.getHours()+'시',
            'congest_lvl' : '예상 혼잡도: '+fcst_data['fcst_congest_lvl'],
            'ppltn_range' : '예상 인구수: ' ,
            'ppltn_max' : ppltn_max,
            'ppltn_min' : ppltn_min,
            'color' : color,
        }
    })
}

Highcharts.chart('congest_bar_chart', {
    chart: {
        type: 'column'
    },
    title: {
        text: ''
    },
    // subtitle: {
    //     text: 'Source: <a href="https://worldpopulationreview.com/world-cities" target="_blank">World Population Review</a>'
    // },
    xAxis: {
        //type: 'category',
        categories: category_list,
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
            text: 'Population (thousand)'
        }
    },
    legend: {
        enabled: false
    },
    tooltip: {
        headerFormat: '',
        pointFormat: '{point.custom.time}<br> \
                        <span class="text">{point.custom.congest_lvl}</span>\
                        <div style="display:inline-block;width: 20px;height: 20px;border-radius: 50%;background-color: {point.custom.color};"></div><br>\
                        {point.custom.ppltn_range} <b>{point.custom.ppltn_min} ~ {point.custom.ppltn_max}</b>'
    },
    series: [{
        name: 'Population',
        colors: color_list,
        colorByPoint: true,
        groupPadding: 0,
        data: data_list
        ,
        dataLabels: {
            enabled: false,
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

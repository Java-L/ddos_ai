const myChart = echarts.init(document.getElementById('chart-container'));
// Configure chart
const option = {
    // ... Configure chart based on returned data ...
    series: [{
        name: 'Accuracy',
        type: 'gauge',
        detail: {formatter: '{value}%'},
        data: [{value: '{{ overall_accuracy }}'}],
    }]
};
myChart.setOption(option);

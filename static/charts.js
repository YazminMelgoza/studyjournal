var result;

function getChartData() {
    $.ajax({
        url: "/getChartData",
        dataType: "json",
        type: "get",
        error: function(event){
            console.log('An error ocurred while getting chart data')
            event.preventDefault;
        }
    })
    .done(function(data) {
        // data is stored in variable result
        result = data;
        for (let i = 1; i < 8; i++) {
            result[i][0] = new Date(result[i][0].split("-"));
        }
        google.charts.setOnLoadCallback(drawChart);
    });
}
function drawChart() {
    // Define the chart to be drawn.
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Day');
    data.addColumn('number', 'Hours');
    data.addRows(
      result.slice(1)
    );
    var options = {
        title: 'My Study Hours this Week',
        titleTextStyle: { color: 'white',
                          fontSize: 20,
                          bold: false },
        hAxis: { format: 'MMM dd', 
                 gridlines: { color: '#9c9bf1'},
                 textStyle: { color: 'white'} },
        legend: { position: "none"},
        baselineColor: '#9c9bf1',
        backgroundColor: { fill: 'transparent'},
        colors: ['white'],
        vAxis: { gridlines: { color: '#9c9bf1'},
                 textStyle: { color: 'white'} },
    };
    
    // Instantiate and draw the chart.
    var chart = new google.visualization.ColumnChart(document.getElementById('myColumnChart'));
    chart.draw(data, options);
  }
$(function() {

    getChartData();
    google.charts.load('current', {packages: ['corechart']});
    
})


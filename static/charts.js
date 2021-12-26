var result, pieChartData;

function getChartData() {
    $.ajax({
        url: "/getChartData",
        dataType: "json",
        type: "get",
        error: function(event){
            console.log('An error ocurred while getting chart data');
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

function getPieChartData() {
    $.ajax({
        url: "/getPieChartData",
        dataType: "json",
        type: "get",
        error: function(event) {
            console.log("An error ocurred while getting pie chart data");
            event.preventDefault;
        }
    }).done(function(data){
        pieChartData = data;
        google.charts.setOnLoadCallback(drawPieChart);
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
        title: 'My Study Hours the last 7 days',
        titleTextStyle: { color: 'white',
                          fontSize: 20,
                          bold: false },
        hAxis: { format: 'EEE dd', 
                 gridlines: { color: '#9c9bf1'},
                 textStyle: { color: 'white'} },
        legend: { position: "none"},
        baselineColor: '#9c9bf1',
        chartArea: {width: '90%', height:'75%'},
        width: '90%',
        height: '100%',
        backgroundColor: 'transparent',
        colors: ['white'],
        vAxis: { gridlines: { color: '#9c9bf1'},
                 textStyle: { color: 'white'} },
        
    };
    
    // Instantiate and draw the chart.
    var chart = new google.visualization.ColumnChart(document.getElementById('myColumnChart'));
    chart.draw(data, options);
  }

function drawPieChart() {
    var data = google.visualization.arrayToDataTable(pieChartData['data']);

    var options = {
        title: 'Today\'s tasks',
        titleTextStyle: { color: 'white',
                          fontSize: 21,
                          bold: false },
        slices: pieChartData['slicesColor'],
        backgroundColor: 'transparent',
        chartArea: {width: '100%', height:'80%'},
        width: '100%',
        height: '100%',
        legend: {textStyle: {color: 'white', fontSize: 16}},
        pieSliceTextStyle: {color: 'black'},
        pieSliceBorderColor: 'transparent'
    };

    var piechart = new google.visualization.PieChart(document.getElementById("myPieChart"));
    piechart.draw(data, options)
}
$(function() {
    google.charts.load('current', {packages: ['corechart']});
    getChartData();
    getPieChartData();
})



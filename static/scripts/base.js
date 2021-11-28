function onInventoryQuickUpdate(id) {
    var amount = $('#amount_' + id).val();
    $('#update_' + id).attr('href', "/inventory/quick_edit/" + id + "/" + amount + "/");
}

function drawChart(list) {

    // Define the chart to be drawn.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Item');
    data.addColumn('number', 'Amount');

    for (var i = 0; i < list.length; i++) {
        var temp = [];
        temp.push(item_list[i].fields.name);
        temp.push(item_list[i].fields.count);
  
        data.addRow(temp);
    }

    var options = { 'height': 400, 'is3D': true, colors: ['#283142',] };
    // '#82e1f5'
    // '#e5656d'
    // '#ffc107'
    // '#4a90ed'
    // '#283142'

    var chart = new google.visualization.BarChart(document.getElementById("inventoryPieChart"));
    chart.draw(data, options);
}

function getInventoryList() {
    // Get data by ajax call
    $.getJSON('/inventory/inventory_list/', function(data, jqXHR) {
        item_list = jQuery.parseJSON(data.inventory_list);
        // console.log(item_list);
        // for (var i = 0; i < item_list.length; i++) {
        //     console.log(item_list[i].fields.name);
        //     console.log(item_list[i].fields.count);
        // }
        drawChart(item_list);
    });
}

$(document).ready(function() {
    google.charts.load('current', {packages: ['corechart']});
    google.charts.setOnLoadCallback(getInventoryList);
});

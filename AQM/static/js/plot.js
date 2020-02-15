$('#measurement').on('change',function(){

    $.ajax({
        url: "/plot",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'measurement': document.getElementById('measurement').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('chart', data );
        }
    });
})
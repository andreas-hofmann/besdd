function load_time_graph(element, url, get) {
    $.get(url, get,
        function(data) {
            Plotly.newPlot(element, [
                    { name: 'Night (h)', y: data['night_h'], text: data['night_cnt'], marker: { color:'rgb(100,000,230)' }, x: data['day'], type: 'bar'  },
                    { name: 'Day (h)',   y: data['day_h'],   text: data['day_cnt'],   marker: { color:'rgb(245,200,050)' }, x: data['day'], type: 'bar'  },
                    { name: 'Total (h)', y: data['sum_h'],   text: data['sum_cnt'],   mode: 'markers', marker: { color:'rgb(000,000,000)' }, x: data['day'], type: 'scatter' },
                    { name: 'Diapers',   y: data['diapers'],                          mode: 'markers', marker: { color:'rgb(0,200,050)' }, x: data['day'], type: 'scatter'  },
                    { name: 'Meals',     y: data['meals'],                            mode: 'markers', marker: { color:'rgb(245,0,050)' }, x: data['day'], type: 'scatter'  },
                ], {
                    yaxis: {
                        showticklabels:true,
                    },
                    barmode:'stack',
                },{
                    displayModeBar: false,
                    responsive: true,
                }
            );
        }
    );
}

function load_histogram(element, url, get) {
    $.get(url, get,
        function(data) {
            Plotly.newPlot(element, [
                    { name: 'Sleep',   type: 'histogram', histfunc: "sum", x: data['time'], y: data['sleep'] },
                    { name: 'Meals',   type: 'histogram', histfunc: "sum", x: data['time'], y: data['meals'] },
                    { name: 'Diapers', type: 'histogram', histfunc: "sum", x: data['time'], y: data['diapers'] },
                ], {
                    xaxis: {
                        autotick:false,
                        tick0:0,
                        dtick:6
                    },
                    yaxis: {
                        showticklabels:false,
                    }
                },{
                    displayModeBar: false,
                    responsive: true,
                }
            );
        }
    );
}

function since_str(data) {
    str = "";

    if (data['since_d'] != 0) {
      str += " " + data['since_d'] + " day"
      if (data['since_d'] > 1) {
        str += "s"
      }
    }
    if (data['since_h'] != 0) {
      str += " " + data['since_h'] + " hour";
      if (data['since_h'] > 1) {
        str += "s"
      }
    }
    if (data['since_m'] != 0) {
      str += " " + data['since_m'] + " minute";
      if (data['since_m'] > 1) {
        str +=  "s"
      }
    }
    return str;
}
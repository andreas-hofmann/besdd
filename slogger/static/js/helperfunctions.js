function load_percentile_graph(element, url, get, options) {
    $.get(url, get)
        .done( function(data) {
            Plotly.newPlot(element, [
                    { name: 'value', y: data['value'], marker: { color:'blue' }, x: data['day'], type: 'lines', mode: 'markers', marker: { size: 10, }, },
                    { name: 'p5', y: data['p5'],   x: data['day'], type: 'lines', line: { dash: 'dashdot', shape: 'spline', width: 1, color: 'red', }, },
                    { name: 'p10', y: data['p10'], x: data['day'], type: 'lines', line: { dash: 'dot',     shape: 'spline', width: 1, color: 'orange', }, },
                    { name: 'p25', y: data['p25'], x: data['day'], type: 'lines', line: { dash: 'dashdot', shape: 'spline', width: 1, color: 'grey', }, },
                    { name: 'p50', y: data['p50'], x: data['day'], type: 'lines', line: { dash: 'solid',   shape: 'spline', width: 1, color: 'black', }, },
                    { name: 'p75', y: data['p75'], x: data['day'], type: 'lines', line: { dash: 'dashdot', shape: 'spline', width: 1, color: 'grey', }, },
                    { name: 'p90', y: data['p90'], x: data['day'], type: 'lines', line: { dash: 'dot',     shape: 'spline', width: 1, color: 'orange', }, },
                    { name: 'p95', y: data['p95'], x: data['day'], type: 'lines', line: { dash: 'dashdot', shape: 'spline', width: 1, color: 'red', }, },
                ], {
                    yaxis: {
                        showticklabels:true,
                    },
                    xaxis: {
                        title: 'Age (days)',
                    },
                },{
                    displayModeBar: false,
                    responsive: true,
                }
            );
        })
        .fail(function() {
            alert("Error fetching data!");
        })
        .always(function() {
            vm.updateDone();
        }
    );
}

function load_measurement_graph(element, url, get, options) {
    $.get(url, get)
        .done( function(data) {
            Plotly.newPlot(element, [
                    { name: 'Height', y: data['height'], connectgaps:true, marker: { color:'blue' },  x: data['age_weeks'], mode:'lines+markers', line: { dash: 'dot', shape: 'spline', width: 1, color: 'grey', } },
                    { name: 'Weight', y: data['weight'], connectgaps:true, marker: { color:'green' }, x: data['age_weeks'], mode:'lines+markers', line: { dash: 'dot', shape: 'spline', width: 1, color: 'grey', } },
                    { name: 'Events', y: data['nr_events'], x: data['age_weeks'], type:'histogram', histfunc:'sum', opacity:0.3, marker: { color:'red' }, },
                ], {
                    yaxis: {
                        showticklabels:true,
                    },
                    xaxis: {
                        title: 'Age (weeks)',
                    },
                },{
                    displayModeBar: false,
                    responsive: true,
                }
            );
        })
        .fail(function() {
            alert("Error fetching data!");
        })
        .always(function() {
            vm.updateDone();
        }
    );
}

function load_time_graph(element, url, get, options) {
    $.get(url, get)
        .done( function(data) {
            Plotly.newPlot(element, [
                    { name: 'Night (h)', y: data['night_h'], text: data['night_cnt'], marker: { color:'rgb(100,000,230)' }, x: data['day'], type: 'bar', visible: options.plots.sleep,  },
                    { name: 'Day (h)',   y: data['day_h'],   text: data['day_cnt'],   marker: { color:'rgb(245,200,050)' }, x: data['day'], type: 'bar', visible: options.plots.sleep,  },
                    { name: 'Total (h)', y: data['sum_h'],   text: data['sum_cnt'],   mode: 'markers', marker: { color:'rgb(000,000,000)' }, x: data['day'], type: 'scatter', visible: options.plots.sleep, },
                    { name: 'Diapers',   y: data['diapers'],                          mode: 'markers', marker: { color:'rgb(0,200,050)' },   x: data['day'], type: 'scatter', visible: options.plots.diapers  },
                    { name: 'Meals',     y: data['meals'],                            mode: 'markers', marker: { color:'rgb(245,0,050)' },   x: data['day'], type: 'scatter', visible: options.plots.meals, },
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
        })
        .fail(function() {
            alert("Error fetching data!");
        })
        .always(function() {
            vm.updateDone();
        }
    );
}

function load_histogram(element, url, get, options) {
    $.get(url, get)
        .done(function(data) {
            Plotly.newPlot(element, [
                    { name: 'Sleep',   type: 'histogram', histfunc: "sum", x: data['time'], y: data['sleep'],   visible: options.plots.sleep },
                    { name: 'Meals',   type: 'histogram', histfunc: "sum", x: data['time'], y: data['meals'],   visible: options.plots.meals },
                    { name: 'Diapers', type: 'histogram', histfunc: "sum", x: data['time'], y: data['diapers'], visible: options.plots.diapers },
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
        })
        .fail(function() {
            alert("Error fetching data!");
        })
        .always(function() {
            vm.updateDone();
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
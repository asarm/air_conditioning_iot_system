import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np

import requests

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

line_chart_style = {"width": "65%"}
gauge_chart_style = {"width": "40%"}

def get_sliders():
    return html.Div([
            # temperature selection
            html.Div([
                html.H5("Desired Temperature Range", style={"padding-left": "4%"}),
                dcc.RangeSlider(
                    -5, 50,
                    id="temp-slider",
                    value=[15, 25],
                    tooltip={"placement": "bottom", "always_visible": True},
                    marks={
                        -5: {'label': '-5°C', 'style': {'color': 'blue'}},
                        0: {'label': '0°C', 'style': {'color': '#77b0b1'}},
                        20: {'label': '20°C', 'style': {'color': '#82b83d'}},
                        30: {'label': '30°C', 'style': {'color': '#f59b42'}},
                        50: {'label': '50°C', 'style': {'color': '#eb2d17'}},
                    }
                ),        
            ], style={"width": "30%", "justify-content": "center", "margin": "auto"}),        

            # status
            dbc.Button(
                [
                    "Status",
                    dbc.Badge("Off", color="light", text_color="dark", className="ms-1", id="status-text"),
                ],
                id="status-btn",
                color="primary",                
                style={"margin": "auto", "justify-content": "center"}
            ),

            # humidity selection
            html.Div([
                html.H5("Desired Humidity Range", style={"padding-left": "4%"}),
                dcc.RangeSlider(
                    0, 100,
                    id="hum-slider",
                    value=[45, 70],
                    tooltip={"placement": "bottom", "always_visible": True},
                    marks={
                        0: {'label': '0', 'style': {'color': 'blue'}},
                        20: {'label': '20', 'style': {'color': 'blue'}},
                        40: {'label': '40', 'style': {'color': '#82b83d'}},
                        60: {'label': '60', 'style': {'color': '#82b83d'}},
                        80: {'label': '80', 'style': {'color': '#eb2d17'}},
                        100: {'label': '100', 'style': {'color': '#eb2d17'}},
                    }
                ),        
            ], style={"width": "30%", "justify-content": "center", "margin": "auto"}),
            ], style={"display": "flex", "padding-top": "5%", "background-color": "white"})

app.layout = html.Div([
    get_sliders(),
    html.Div([
        dcc.Graph(
            id='temp-data',
            style=line_chart_style,
            config={
                'displayModeBar': False
            }
        ),

        dcc.Graph(
            id="temp-gauge",
            style=gauge_chart_style,
            config={
                'displayModeBar': False
            }
        )

    ], style={"display": "flex"}),

    html.Div([
        dcc.Graph(        
            id='hum-data',
            style=line_chart_style,
            config={
                    'displayModeBar': False
                }            
        ),
        dcc.Graph(
            id="hum-gauge",
            style=gauge_chart_style,
            config={
                'displayModeBar': False
            }            
        )        
    ], style={"display": "flex"}),

    dcc.Interval(id="interval", interval=2000), # 5 secs
])


def get_status(range, data):
    std = np.std(data)
    mean_val = np.mean(data)
    max_val = np.max(data)
    min_val = np.min(data) 

    lower_bound = range[0]
    upper_bound = range[1]
    
    value = data[-1]

    main_color = "primary"

    if value > mean_val + (std*1.5) or value < mean_val - (std*1.5): 
        main_color = "danger"
    elif value < lower_bound:
        main_color = "success"
    elif value > upper_bound:
        main_color = "success"

    return main_color


def get_prediction(data, weights, horizon, window_size):
    predictions = []
    for i in range(horizon):    
        if i > 0:
            window_data = data[-window_size+1:]    
            window_data.append(predictions[-1])
        else:
             window_data = data[-window_size:]

        avg = np.dot(window_data, weights) / np.sum(weights)

        predictions.append(avg)

    return predictions


def get_line_chart(times, data, title, ranges=(15, 30)):
    alpha = 0.15
    window_size = 20
    weights = [alpha * (1 - alpha) ** i for i in range(1, window_size + 1)]
    horizon = 5

    predictions = get_prediction(data, weights, horizon, window_size)

    # Combine historical and predicted timestamps for continuous x-axis
    all_times = np.concatenate([times, np.arange(int(times[-1]) + 1, int(times[-1]) + 6)])

    original = go.Scatter(
        x=all_times[-25:-5],
        y=data[-20:],
        name=title,
        mode='lines+markers',  # Use lines and markers for clarity
        marker=dict(color='blue')  # Use distinct color for historical data
    )

    prediction_times = all_times[-5:]

    std_dev = np.std(data)
    upper_bound_values = [predictions[0], predictions[-1] + (std_dev*0.75)]
    lower_bound_values = [predictions[0], predictions[-1] - (std_dev*0.75)]

    upper = go.Scatter(
        x=[prediction_times[0], prediction_times[-1]],
        y=upper_bound_values,
        mode='lines',
        line=dict(color='rgba(0,0,0,0.3)'),
        name="Upper Bound",
        fill=None,
        showlegend=False
    )

    lower = go.Scatter(
        x=[prediction_times[0], prediction_times[-1]],
        y=lower_bound_values,
        mode='lines',
        line=dict(color='rgba(0,0,0,0.3)'),
        name="Prediction",
        fill="tonexty",
        showlegend=False
    )

    connecting = go.Scatter(
            x=[times[-1], prediction_times[0]],
            y=[data[-1], predictions[0]],
            mode='lines',
            line=dict(color='gray'),
            showlegend=False
        )        
    fig = go.Figure(data=[original, upper, lower, connecting])
    fig.add_hline(ranges[0], line_color="#ff4d4d", line_dash="dash")
    fig.add_hline(ranges[1], line_color="#ff4d4d", line_dash="dash")
    fig.update_layout(paper_bgcolor = "white", font = {'color': "black", 'family': "Arial"})

    return fig


def get_gauge_chart(title, data):
    std = np.std(data)
    mean_val = np.mean(data)
    max_val = np.max(data)
    min_val = np.min(data) 
    
    print(title, [mean_val-(std*1.5), 0])
    fig = go.Figure(
        go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = data[-1],
        mode = "gauge+number+delta",
        title = {'text': title},
        delta = {'reference': data[-2]}, # prev val
        gauge = {'axis': {'range': [min_val-(std*2), max_val+(std*2)]},
                'steps' : [
                    {'range': [min_val-(std*2), mean_val-(std*1.5)], 'color': "red"},
                    {'range': [mean_val-(std*1.5), mean_val+(std*0.75)], 'color': "lightgray"},
                    {'range': [mean_val+(std*0.75), mean_val+(std*1.5)], 'color': "gray"},
                    {'range': [mean_val+(std*1.5), max_val+(std*2)], 'color': "red"}
                    ],
                }))
    fig.update_layout(paper_bgcolor = "white", font = {'color': "black", 'family': "Arial"})

    return fig


@dash.callback(
    Output("temp-data", "figure"),
    Output("hum-data", "figure"),
    Output("temp-gauge", "figure"),
    Output("hum-gauge", "figure"),
    Output("status-btn", "color"),
    Output("status-text", "children"),
    Input("interval", "n_intervals"),
    Input("temp-slider", "value"),
    Input("hum-slider", "value"),
)
def live_data(n_intervals, temp_range, hum_range):
    resp = requests.get("http://127.0.0.1:5000/get").json()["data"]
    times = []
    hums = []
    temps = []

    print("Response", resp)
    for line in resp:
        times.append(line["id"])
        hums.append(line["hum"])
        temps.append(line["temp"])

    temp_line = get_line_chart(times, temps, "Temperature", ranges=temp_range)
    hum_line = get_line_chart(times, hums, "Humidity", ranges=hum_range)

    temp_gauge = get_gauge_chart(title="Temperature", data=temps)
    hum_gauge = get_gauge_chart(title="Humidity", data=hums)
    
    status_btn_color = "primary"
    status = "Off"

    status_btn_color_hum = get_status(hum_range, hums)
    status_btn_color_temp = get_status(temp_range, temps)

    if "danger" in {status_btn_color_hum, status_btn_color_temp}:
        status_btn_color = "danger"
        status = "Alert"
    elif "success" in {status_btn_color_hum, status_btn_color_temp}:
        status_btn_color = "success"
        status = "On"


    return temp_line, hum_line, temp_gauge, hum_gauge, status_btn_color, status


if __name__ == '__main__':
    app.run(debug=True)

import pendulum
from dash import Dash, html, dash_table, dcc, Output, Input, callback
import pandas as pd
import plotly.graph_objects as go

from shouldigetaheatpump import get_data

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div(
    [
        html.Div(children="Should I Get a Heat Pump?"),
        html.Hr(),
        html.Div(
            children=[
                html.H4(
                    "Enter a location:",
                    style={
                        "display": "inline-block",
                        "margin-right": 20,
                        # "border": "1px solid black",
                    },
                ),
                dcc.Input(
                    id="lat-long",
                    type="text",
                    placeholder="lattitude, longitude",
                    debounce=True,
                ),
            ]
        ),
        html.Div(
            children=[
                "Hourly temperature",
                dcc.Graph(figure={}, id="temperature"),
                "Enter monthly heat usage:",
            ]
        ),
    ]
)
# 51.11488758418279, -114.06747997399614


@callback(
    Output(component_id="temperature", component_property="figure"),
    Input(component_id="lat-long", component_property="value"),
)
def update_graph(lat_long: str | None):
    if not lat_long:
        return {}
    lat, long = (float(x) for x in lat_long.split(","))

    end = pendulum.now() - pendulum.duration(days=10)
    start = end - pendulum.duration(years=1)

    temperatures = get_data.get_weather_data(lat=lat, long=long, start=start, end=end)
    daily_mean = temperatures.groupby(by=temperatures["date"].dt.date).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=temperatures["date"],
            y=temperatures["temperature"],
            mode="markers",
            name="Hourly Temperature",
            marker=dict(size=5, color="#35F0BF"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_mean["date"],
            y=daily_mean["temperature"],
            mode="lines",
            name="Daily Average",
            marker=dict(color="#35BBF0"),
        )
    )
    fig.update_xaxes(range=[start, end])

    return fig


if __name__ == "__main__":
    import os

    app.run(debug=False, use_reloader=True)

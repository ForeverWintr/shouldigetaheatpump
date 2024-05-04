import pendulum
from dash import Dash, html, dash_table, dcc, Output, Input, callback
import pandas as pd
import plotly.express as px

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
        html.Div("Hourly temperature"),
        dcc.Graph(figure={}, id="temperature"),
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

    end = pendulum.Date.today() - pendulum.duration(days=10)
    start = end - pendulum.duration(years=1)

    temperatures = get_data.get_weather_data(lat=lat, long=long, start=start, end=end)

    fig = px.scatter(temperatures.set_index("date"))
    return fig


if __name__ == "__main__":
    import os

    app.run(debug=False, use_reloader="WINGDB_ACTIVE" not in os.environ)

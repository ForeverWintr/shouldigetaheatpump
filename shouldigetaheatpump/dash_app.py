from dash import Dash, html, dash_table, dcc
import pandas as pd

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
                    id="lat-long", type="text", placeholder="lattitude, longitude"
                ),
            ]
        ),
        dcc.Graph(figure={}, id="temperature"),
    ]
)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

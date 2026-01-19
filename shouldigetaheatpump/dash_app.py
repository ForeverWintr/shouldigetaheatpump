import pendulum
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc
import dash_leaflet as dl

from shouldigetaheatpump import get_data

# Initialize the app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Should I Get a Heat Pump?",
                    className="text-center my-4"
                )
            )
        ),

        # Location input card
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Select Location", className="card-title mb-3"),
                            dbc.Label("Enter coordinates or click on the map below:"),
                            dbc.Input(
                                id="lat-long",
                                type="text",
                                placeholder="latitude, longitude (e.g., 51.1149, -114.0675)",
                                debounce=True,
                                className="mb-2",
                            ),
                        ]
                    ),
                    className="mb-4 shadow-sm"
                ),
                width=12
            )
        ),

        # Map card
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Interactive Map", className="card-title mb-3"),
                            dl.Map(
                                id="location-map",
                                center=[51.1149, -114.0675],
                                zoom=10,
                                children=[
                                    dl.TileLayer(),
                                ],
                                style={'width': '100%', 'height': '500px', 'border-radius': '0.25rem'},
                            ),
                        ]
                    ),
                    className="mb-4 shadow-sm"
                ),
                width=12
            )
        ),

        # Temperature graph card
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Temperature Analysis", className="card-title mb-3"),
                            dcc.Graph(figure={}, id="temperature"),
                        ]
                    ),
                    className="mb-4 shadow-sm"
                ),
                width=12
            )
        ),
    ],
    fluid=True,
    className="px-4"
)
# 51.11488758418279, -114.06747997399614


@callback(
    Output(component_id="lat-long", component_property="value"),
    Output(component_id="location-map", component_property="children"),
    Input(component_id="location-map", component_property="clickData"),
)
def map_click(click_data):
    """Update text input and map marker when map is clicked."""
    if not click_data:
        # Return TileLayer only (no marker)
        return None, [dl.TileLayer()]

    # Extract lat/lng from clickData dictionary
    lat = click_data['latlng']['lat']
    lng = click_data['latlng']['lng']

    # Format as "lat, lng" string for text input
    lat_long_str = f"{lat}, {lng}"

    # Create marker at clicked location
    marker = dl.Marker(
        position=[lat, lng],
        children=[
            dl.Tooltip("Selected Location"),
            dl.Popup(f"{lat:.4f}°, {lng:.4f}°")
        ]
    )

    # Return updated text input and map children (TileLayer + Marker)
    return lat_long_str, [dl.TileLayer(), marker]


@callback(
    Output(component_id="location-map", component_property="children", allow_duplicate=True),
    Input(component_id="lat-long", component_property="value"),
    prevent_initial_call=True,
)
def text_input_to_map(lat_long: str | None):
    """Update map marker when text input changes."""
    if not lat_long:
        # No marker if input is empty
        return [dl.TileLayer()]

    try:
        lat, lng = (float(x.strip()) for x in lat_long.split(","))

        # Create marker at specified coordinates
        marker = dl.Marker(
            position=[lat, lng],
            children=[
                dl.Tooltip("Selected Location"),
                dl.Popup(f"{lat:.4f}°, {lng:.4f}°")
            ]
        )

        return [dl.TileLayer(), marker]
    except (ValueError, AttributeError):
        # Invalid input - return just TileLayer (no marker)
        return [dl.TileLayer()]


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
    fig.update_xaxes(range=[start, end], title="Date")
    fig.update_yaxes(title="Temperature (°C)")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode='x unified'
    )

    return fig


if __name__ == "__main__":
    app.run(debug=False, use_reloader=True)

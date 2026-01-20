import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pendulum
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

from shouldigetaheatpump import get_data

# Initialize the app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,  # Add for moon/sun icons
    ],
)

# App layout
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(html.H1("Should I Get a Heat Pump?", className="text-center my-4"))
        ),
        # Theme toggle row
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Label(className="fa fa-moon", html_for="theme-switch"),
                        dbc.Switch(
                            id="theme-switch",
                            value=True,  # True = light, False = dark
                            persistence=True,
                            className="d-inline-block ms-1 me-1",
                        ),
                        dbc.Label(className="fa fa-sun", html_for="theme-switch"),
                    ],
                    className="d-flex justify-content-end align-items-center mb-3",
                ),
                width=12,
            )
        ),
        # Map card
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Select Location", className="card-title mb-3"),
                            dbc.Label("Click on the map to select a location:"),
                            dl.Map(
                                id="location-map",
                                center=[51.1149, -114.0675],
                                zoom=10,
                                children=[
                                    dl.TileLayer(),
                                ],
                                style={
                                    "width": "100%",
                                    "height": "500px",
                                    "border-radius": "0.25rem",
                                },
                            ),
                            html.Div(
                                id="coordinates-display",
                                className="mt-3 text-muted",
                                children="Click on the map to select coordinates",
                            ),
                        ]
                    ),
                    className="mb-4 shadow-sm",
                ),
                width=12,
            )
        ),
        # Hidden storage for coordinates
        dcc.Store(id="lat-long-store"),
        dcc.Store(id="theme-store", storage_type="local", data=True),  # True = light
        # Temperature graph card
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(
                                "Temperature Analysis", className="card-title mb-3"
                            ),
                            dcc.Loading(
                                id="loading-graph",
                                type="default",
                                children=dcc.Graph(figure={}, id="temperature"),
                            ),
                        ]
                    ),
                    className="mb-4 shadow-sm",
                ),
                width=12,
            )
        ),
    ],
    fluid=True,
    className="px-4",
)
# 51.11488758418279, -114.06747997399614

# Clientside callback for instant theme switching
app.clientside_callback(
    """
    function(switchValue) {
        const theme = switchValue ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', theme);
        return window.dash_clientside.no_update;
    }
    """,
    Output("theme-switch", "id"),  # Dummy output
    Input("theme-switch", "value"),
)


@callback(
    Output(component_id="lat-long-store", component_property="data"),
    Output(component_id="location-map", component_property="children"),
    Input(component_id="location-map", component_property="clickData"),
)
def map_click(click_data):
    """Update stored coordinates and map marker when map is clicked."""
    if not click_data:
        # Return no data and TileLayer only (no marker)
        return None, [dl.TileLayer()]

    # Extract lat/lng from clickData dictionary
    lat = click_data["latlng"]["lat"]
    lng = click_data["latlng"]["lng"]

    # Store coordinates as dict
    coords_data = {"lat": lat, "lng": lng}

    # Create marker at clicked location
    marker = dl.Marker(
        position=[lat, lng],
        children=[dl.Tooltip("Selected Location"), dl.Popup(f"{lat:.4f}°, {lng:.4f}°")],
    )

    # Return stored data and map children (TileLayer + Marker)
    return coords_data, [dl.TileLayer(), marker]


@callback(
    Output(component_id="coordinates-display", component_property="children"),
    Input(component_id="lat-long-store", component_property="data"),
)
def update_coordinates_display(coords_data):
    """Update the displayed coordinates text."""
    if not coords_data:
        return "Click on the map to select coordinates"

    lat = coords_data["lat"]
    lng = coords_data["lng"]
    return f"Selected coordinates: {lat:.4f}°, {lng:.4f}°"


@callback(
    Output(component_id="temperature", component_property="figure"),
    Input(component_id="lat-long-store", component_property="data"),
    Input(component_id="theme-switch", component_property="value"),
)
def update_graph(coords_data, is_light_mode):
    # Theme-aware color palettes
    if is_light_mode:
        hourly_color = "#35F0BF"  # Cyan
        daily_color = "#35BBF0"  # Blue
        grid_color = "rgba(0, 0, 0, 0.1)"
        font_color = "#212529"
    else:
        hourly_color = "#4DFFD7"  # Lighter cyan for dark backgrounds
        daily_color = "#5CD4FF"  # Lighter blue for dark backgrounds
        grid_color = "rgba(255, 255, 255, 0.1)"
        font_color = "#f8f9fa"

    # Return empty figure with theme-aware styling if no location selected
    if not coords_data:
        fig = go.Figure()
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color=font_color),
            margin=dict(l=50, r=50, t=30, b=50),
            xaxis=dict(gridcolor=grid_color, showticklabels=False),
            yaxis=dict(gridcolor=grid_color, showticklabels=False),
        )
        return fig

    lat = coords_data["lat"]
    long = coords_data["lng"]

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
            marker=dict(size=5, color=hourly_color),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_mean["date"],
            y=daily_mean["temperature"],
            mode="lines",
            name="Daily Average",
            marker=dict(color=daily_color),
        )
    )
    fig.update_xaxes(range=[start, end], title="Date", gridcolor=grid_color)
    fig.update_yaxes(title="Temperature (°C)", gridcolor=grid_color)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color=font_color),
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode="x unified",
    )

    return fig


if __name__ == "__main__":
    app.run(debug=False, use_reloader=True)

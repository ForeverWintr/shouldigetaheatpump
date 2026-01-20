"""Unit tests for Dash app callbacks."""

from unittest.mock import patch

import pandas as pd

from shouldigetaheatpump.dash_app import (
    map_click,
    trigger_geolocation,
    update_button_state,
    update_coordinates_display,
    update_graph,
    update_location_from_geolocation,
)


class TestMapClickCallback:
    """Test the map_click callback function."""

    def test_map_click_with_valid_data(self):
        """Test that clicking the map updates coordinates and adds a marker."""
        click_data = {"latlng": {"lat": 51.1149, "lng": -114.0675}}

        coords_data, map_children = map_click(click_data)

        # Check coordinates are stored correctly
        assert coords_data == {"lat": 51.1149, "lng": -114.0675}

        # Check map children includes TileLayer and Marker
        assert len(map_children) == 2
        assert map_children[0].__class__.__name__ == "TileLayer"
        assert map_children[1].__class__.__name__ == "Marker"

        # Check marker position
        assert map_children[1].position == [51.1149, -114.0675]

    def test_map_click_with_no_data(self):
        """Test that no click returns None and TileLayer only."""
        coords_data, map_children = map_click(None)

        assert coords_data is None
        assert len(map_children) == 1
        assert map_children[0].__class__.__name__ == "TileLayer"


class TestUpdateCoordinatesDisplay:
    """Test the update_coordinates_display callback function."""

    def test_display_with_valid_coords(self):
        """Test that coordinates are formatted correctly for display."""
        coords_data = {"lat": 51.1149, "lng": -114.0675}

        result = update_coordinates_display(coords_data)

        assert result == "Selected coordinates: 51.1149°, -114.0675°"

    def test_display_with_no_coords(self):
        """Test default message when no coordinates are selected."""
        result = update_coordinates_display(None)

        assert result == "Click on the map to select coordinates"

    def test_display_with_precise_coords(self):
        """Test that coordinates are displayed with 4 decimal places."""
        coords_data = {"lat": 51.114887583, "lng": -114.067479974}

        result = update_coordinates_display(coords_data)

        assert result == "Selected coordinates: 51.1149°, -114.0675°"


class TestUpdateGraphCallback:
    """Test the update_graph callback function."""

    def test_graph_with_no_coords(self):
        """Test that styled empty graph is returned when no coordinates."""
        result = update_graph(None, True)

        # Should return a figure (not empty dict)
        assert "layout" in result
        assert "data" in result
        # Data should be empty (no traces)
        assert len(result["data"]) == 0
        # Layout should have theme-aware styling
        assert result["layout"]["plot_bgcolor"] == "rgba(0,0,0,0)"
        assert result["layout"]["paper_bgcolor"] == "rgba(0,0,0,0)"
        assert result["layout"]["font"]["color"] == "#212529"  # Light mode

    def test_graph_with_no_coords_dark_mode(self):
        """Test that empty graph uses dark mode colors when theme is dark."""
        result = update_graph(None, False)

        # Should return a figure with dark mode styling
        assert "layout" in result
        assert len(result["data"]) == 0
        assert result["layout"]["font"]["color"] == "#f8f9fa"  # Dark mode

    @patch("shouldigetaheatpump.dash_app.get_data.get_weather_data")
    def test_graph_with_valid_coords(self, mock_get_weather_data):
        """Test that graph is generated with valid coordinates."""
        # Mock weather data
        mock_df = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=24, freq="h"),
                "temperature": [i * 0.5 for i in range(24)],
            }
        )
        mock_get_weather_data.return_value = mock_df

        coords_data = {"lat": 51.1149, "lng": -114.0675}

        result = update_graph(coords_data, True)

        # Check that a figure was returned
        assert "data" in result
        assert len(result["data"]) == 2  # Hourly and daily average traces

        # Check that get_weather_data was called with correct params
        mock_get_weather_data.assert_called_once()
        call_kwargs = mock_get_weather_data.call_args.kwargs
        assert call_kwargs["lat"] == 51.1149
        assert call_kwargs["long"] == -114.0675

    @patch("shouldigetaheatpump.dash_app.get_data.get_weather_data")
    def test_graph_has_correct_layout(self, mock_get_weather_data):
        """Test that graph has proper axis labels and styling."""
        # Mock weather data
        mock_df = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=24, freq="h"),
                "temperature": [i * 0.5 for i in range(24)],
            }
        )
        mock_get_weather_data.return_value = mock_df

        coords_data = {"lat": 51.1149, "lng": -114.0675}

        result = update_graph(coords_data, True)

        # Check layout properties
        assert result["layout"]["xaxis"]["title"]["text"] == "Date"
        assert result["layout"]["yaxis"]["title"]["text"] == "Temperature (°C)"
        assert result["layout"]["hovermode"] == "x unified"

    @patch("shouldigetaheatpump.dash_app.get_data.get_weather_data")
    def test_graph_trace_names(self, mock_get_weather_data):
        """Test that graph traces have correct names."""
        # Mock weather data
        mock_df = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=24, freq="h"),
                "temperature": [i * 0.5 for i in range(24)],
            }
        )
        mock_get_weather_data.return_value = mock_df

        coords_data = {"lat": 51.1149, "lng": -114.0675}

        result = update_graph(coords_data, True)

        # Check trace names
        assert result["data"][0]["name"] == "Hourly Temperature"
        assert result["data"][1]["name"] == "Daily Average"

    @patch("shouldigetaheatpump.dash_app.get_data.get_weather_data")
    def test_graph_light_mode_colors(self, mock_get_weather_data):
        """Test that graph uses correct colors in light mode."""
        # Mock weather data
        mock_df = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=24, freq="h"),
                "temperature": [i * 0.5 for i in range(24)],
            }
        )
        mock_get_weather_data.return_value = mock_df

        coords_data = {"lat": 51.1149, "lng": -114.0675}

        result = update_graph(coords_data, is_light_mode=True)

        # Check light mode colors
        assert result["data"][0]["marker"]["color"] == "#35F0BF"  # Hourly cyan
        assert result["data"][1]["marker"]["color"] == "#35BBF0"  # Daily blue
        assert result["layout"]["font"]["color"] == "#212529"  # Dark text
        assert result["layout"]["xaxis"]["gridcolor"] == "rgba(0, 0, 0, 0.1)"
        assert result["layout"]["yaxis"]["gridcolor"] == "rgba(0, 0, 0, 0.1)"

    @patch("shouldigetaheatpump.dash_app.get_data.get_weather_data")
    def test_graph_dark_mode_colors(self, mock_get_weather_data):
        """Test that graph uses correct colors in dark mode."""
        # Mock weather data
        mock_df = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=24, freq="h"),
                "temperature": [i * 0.5 for i in range(24)],
            }
        )
        mock_get_weather_data.return_value = mock_df

        coords_data = {"lat": 51.1149, "lng": -114.0675}

        result = update_graph(coords_data, is_light_mode=False)

        # Check dark mode colors
        assert result["data"][0]["marker"]["color"] == "#4DFFD7"  # Lighter cyan
        assert result["data"][1]["marker"]["color"] == "#5CD4FF"  # Lighter blue
        assert result["layout"]["font"]["color"] == "#f8f9fa"  # Light text
        assert result["layout"]["xaxis"]["gridcolor"] == "rgba(255, 255, 255, 0.1)"
        assert result["layout"]["yaxis"]["gridcolor"] == "rgba(255, 255, 255, 0.1)"


class TestTriggerGeolocationCallback:
    """Test the trigger_geolocation callback function."""

    def test_trigger_with_click(self):
        """Test that clicking button triggers geolocation."""
        result = trigger_geolocation(n_clicks=1)
        assert result is True

    def test_trigger_with_multiple_clicks(self):
        """Test that multiple clicks still trigger geolocation."""
        result = trigger_geolocation(n_clicks=5)
        assert result is True

    def test_trigger_with_zero_clicks(self):
        """Test that zero clicks returns False."""
        result = trigger_geolocation(n_clicks=0)
        assert result is False

    def test_trigger_with_none(self):
        """Test that None clicks returns False."""
        result = trigger_geolocation(n_clicks=None)
        assert result is False


class TestUpdateLocationFromGeolocationCallback:
    """Test the update_location_from_geolocation callback function."""

    def test_successful_position(self):
        """Test that successful position updates store and map."""
        position = {"lat": 51.1149, "lon": -114.0675}

        (
            coords_data,
            viewport,
            map_children,
            alert_msg,
            alert_open,
            alert_color,
        ) = update_location_from_geolocation(position, None)

        # Check coordinates are stored correctly (lon → lng conversion)
        assert coords_data == {"lat": 51.1149, "lng": -114.0675}

        # Check viewport is set correctly for panning
        assert viewport["center"] == [51.1149, -114.0675]
        assert viewport["zoom"] == 12
        assert viewport["transition"] == "flyTo"

        # Check map children includes TileLayer and Marker
        assert len(map_children) == 2
        assert map_children[0].__class__.__name__ == "TileLayer"
        assert map_children[1].__class__.__name__ == "Marker"
        assert map_children[1].position == [51.1149, -114.0675]

        # Check alert is closed
        assert alert_msg == ""
        assert alert_open is False
        assert alert_color == "success"

    def test_permission_denied_error(self):
        """Test that permission denied error shows appropriate message."""
        from dash import no_update

        position_error = {"code": 1}

        (
            coords_data,
            viewport,
            map_children,
            alert_msg,
            alert_open,
            alert_color,
        ) = update_location_from_geolocation(None, position_error)

        # Check that store/map are not updated
        assert coords_data == no_update
        assert viewport == no_update
        assert map_children == no_update

        # Check error message
        assert (
            alert_msg
            == "Permission denied. Please enable location access in your browser."
        )
        assert alert_open is True
        assert alert_color == "danger"

    def test_position_unavailable_error(self):
        """Test that position unavailable error shows appropriate message."""
        position_error = {"code": 2}

        (
            coords_data,
            viewport,
            map_children,
            alert_msg,
            alert_open,
            alert_color,
        ) = update_location_from_geolocation(None, position_error)

        # Check error message
        assert (
            alert_msg
            == "Position unavailable. Please check your device location settings."
        )
        assert alert_open is True
        assert alert_color == "danger"

    def test_timeout_error(self):
        """Test that timeout error shows appropriate message."""
        position_error = {"code": 3}

        (
            coords_data,
            viewport,
            map_children,
            alert_msg,
            alert_open,
            alert_color,
        ) = update_location_from_geolocation(None, position_error)

        # Check error message
        assert alert_msg == "Location request timed out. Please try again."
        assert alert_open is True
        assert alert_color == "danger"

    def test_unknown_error(self):
        """Test that unknown error code shows generic message."""
        position_error = {"code": 999}

        (
            coords_data,
            viewport,
            map_children,
            alert_msg,
            alert_open,
            alert_color,
        ) = update_location_from_geolocation(None, position_error)

        # Check error message
        assert alert_msg == "An error occurred while getting your location."
        assert alert_open is True
        assert alert_color == "danger"

    def test_coordinate_conversion(self):
        """Test that lon is correctly converted to lng in store."""
        position = {"lat": 40.7128, "lon": -74.0060}

        coords_data, _, _, _, _, _ = update_location_from_geolocation(position, None)

        # Verify conversion from lon to lng
        assert "lng" in coords_data
        assert "lon" not in coords_data
        assert coords_data["lng"] == -74.0060


class TestUpdateButtonStateCallback:
    """Test the update_button_state callback function."""

    def test_loading_state(self):
        """Test that button shows loading state when update_now is True."""
        children, disabled = update_button_state(
            update_now=True, position=None, position_error=None
        )

        # Check loading state
        assert len(children) == 2
        assert children[0].className == "fa fa-spinner fa-spin me-2"
        assert children[1] == "Getting location..."
        assert disabled is True

    def test_success_state(self):
        """Test that button restores to normal state after success."""
        position = {"lat": 51.1149, "lon": -114.0675}

        children, disabled = update_button_state(
            update_now=False, position=position, position_error=None
        )

        # Check normal state
        assert len(children) == 2
        assert children[0].className == "fa fa-location-arrow me-2"
        assert children[1] == "Use Current Location"
        assert disabled is False

    def test_success_state_with_update_now(self):
        """Test that button shows normal state when position received even if update_now is True."""
        position = {"lat": 51.1149, "lon": -114.0675}

        children, disabled = update_button_state(
            update_now=True, position=position, position_error=None
        )

        # Check normal state (position takes precedence)
        assert len(children) == 2
        assert children[0].className == "fa fa-location-arrow me-2"
        assert children[1] == "Use Current Location"
        assert disabled is False

    def test_error_state(self):
        """Test that button restores to normal state after error."""
        position_error = {"code": 1}

        children, disabled = update_button_state(
            update_now=False, position=None, position_error=position_error
        )

        # Check normal state
        assert len(children) == 2
        assert children[0].className == "fa fa-location-arrow me-2"
        assert children[1] == "Use Current Location"
        assert disabled is False

    def test_default_state(self):
        """Test that button shows default state when nothing triggered."""
        children, disabled = update_button_state(
            update_now=False, position=None, position_error=None
        )

        # Check default state
        assert len(children) == 2
        assert children[0].className == "fa fa-location-arrow me-2"
        assert children[1] == "Use Current Location"
        assert disabled is False

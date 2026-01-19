"""Unit tests for Dash app callbacks."""

from unittest.mock import patch

import pandas as pd

from shouldigetaheatpump.dash_app import (
    map_click,
    update_coordinates_display,
    update_graph,
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
        """Test that empty graph is returned when no coordinates."""
        result = update_graph(None)

        assert result == {}

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

        result = update_graph(coords_data)

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

        result = update_graph(coords_data)

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

        result = update_graph(coords_data)

        # Check trace names
        assert result["data"][0]["name"] == "Hourly Temperature"
        assert result["data"][1]["name"] == "Daily Average"

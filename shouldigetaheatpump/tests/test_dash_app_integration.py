"""Integration tests for Dash app using dash.testing framework."""

import pytest

from shouldigetaheatpump.dash_app import app


@pytest.mark.integration
class TestDashAppIntegration:
    """Integration tests that run the full Dash app in a browser."""

    def test_app_loads(self, dash_duo):
        """Test that the app starts and renders without errors."""
        dash_duo.start_server(app)

        # Wait for app to load
        dash_duo.wait_for_element("h1", timeout=10)

        # Check that the main heading is present
        heading = dash_duo.find_element("h1")
        assert "Should I Get a Heat Pump?" in heading.text

    def test_map_card_renders(self, dash_duo):
        """Test that the map card renders correctly."""
        dash_duo.start_server(app)

        # Wait for the map to be present
        dash_duo.wait_for_element("#location-map", timeout=10)

        # Check that the card title is present
        assert dash_duo.find_element(".card-title").text == "Select Location"

    def test_coordinates_display_default(self, dash_duo):
        """Test that coordinates display shows default message on load."""
        dash_duo.start_server(app)

        # Wait for coordinates display
        dash_duo.wait_for_element("#coordinates-display", timeout=10)

        coords_display = dash_duo.find_element("#coordinates-display")
        assert "Click on the map to select coordinates" in coords_display.text

    def test_temperature_card_renders(self, dash_duo):
        """Test that the temperature analysis card renders."""
        dash_duo.start_server(app)

        # Wait for temperature graph card
        dash_duo.wait_for_element("#temperature", timeout=10)

        # Check that temperature card is present
        cards = dash_duo.find_elements(".card-title")
        card_titles = [card.text for card in cards]
        assert "Temperature Analysis" in card_titles

    def test_layout_structure(self, dash_duo):
        """Test that the overall layout structure is correct."""
        dash_duo.start_server(app)

        # Wait for page to load
        dash_duo.wait_for_element("h1", timeout=10)

        # Check that Bootstrap container is present
        container = dash_duo.find_element(".container-fluid")
        assert container is not None

        # Check that all three cards are present
        cards = dash_duo.find_elements(".card")
        assert len(cards) == 2  # Map card and temperature card

    def test_no_console_errors(self, dash_duo):
        """Test that there are no JavaScript console errors on page load."""
        dash_duo.start_server(app)

        # Wait for page to load
        dash_duo.wait_for_element("h1", timeout=10)

        # Check for console errors
        # Note: This will fail if there are any console errors
        assert dash_duo.get_logs() == [], "Console errors detected"


@pytest.mark.integration
@pytest.mark.slow
class TestDashAppInteractions:
    """Integration tests for user interactions (slower tests)."""

    @pytest.mark.skip(
        reason="Map click interaction requires more complex Selenium interaction with Leaflet"
    )
    def test_map_click_updates_coordinates(self, dash_duo):
        """Test that clicking the map updates the coordinates display.

        Note: This test is skipped because clicking on a Leaflet map requires
        more complex Selenium interactions. The callback itself is tested in
        unit tests (test_dash_app.py).
        """
        dash_duo.start_server(app)

        # Wait for map to load
        dash_duo.wait_for_element("#location-map", timeout=10)

        # This would require finding the map canvas and simulating a click
        # at specific coordinates, which is complex with Leaflet
        # For now, we test this functionality in unit tests instead
        pass

    def test_page_responsiveness(self, dash_duo):
        """Test that the page is responsive and elements are present."""
        dash_duo.start_server(app)

        # Wait for page to load
        dash_duo.wait_for_element("h1", timeout=10)

        # Check that key elements are visible
        heading = dash_duo.find_element("h1")
        assert heading.is_displayed()

        map_element = dash_duo.find_element("#location-map")
        assert map_element.is_displayed()

        # Temperature graph exists but may be empty until location is selected
        temp_graph = dash_duo.find_element("#temperature")
        assert temp_graph is not None

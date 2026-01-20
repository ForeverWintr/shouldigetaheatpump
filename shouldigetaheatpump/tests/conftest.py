"""Pytest configuration for Dash integration tests."""

import pytest
from selenium.webdriver.chrome.options import Options


def pytest_setup_options():
    """Configure Chrome options for Dash testing.

    This is called by the dash[testing] framework to set up Chrome options.
    Configures headless mode and flags needed for CI environments.
    """
    options = Options()

    # Run in headless mode (no GUI)
    options.add_argument("--headless=new")

    # Flags required for Chrome in CI/containerized environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Suppress logging
    options.add_argument("--log-level=3")

    return options


@pytest.fixture
def dash_duo(dash_duo):
    """Override dash_duo fixture to ensure proper cleanup."""
    yield dash_duo
    # Cleanup is handled by the fixture's context manager

# Should I Get a Heat Pump?

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/ForeverWintr/shouldigetaheatpump/actions/workflows/tests.yml/badge.svg)](https://github.com/ForeverWintr/shouldigetaheatpump/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/ForeverWintr/shouldigetaheatpump/branch/main/graph/badge.svg)](https://codecov.io/gh/ForeverWintr/shouldigetaheatpump)

A Python web application that helps users determine whether installing a heat pump would be beneficial based on historical weather data and heat pump efficiency metrics.

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Install dependencies
uv sync
```

### Running the App

```bash
# Run the Dash web app
uv run python -m shouldigetaheatpump.dash_app
```

The app will be available at http://127.0.0.1:8050/

### Usage

1. Click on the interactive map to select a location
2. The coordinates will be displayed below the map
3. View historical temperature data and heat pump efficiency analysis

## Development

### Testing

The project includes both unit tests and integration tests:

```bash
# Run all tests (excluding integration tests that require chromedriver)
uv run pytest -m "not integration"

# Run only unit tests for the Dash app
uv run pytest shouldigetaheatpump/tests/test_dash_app.py -v

# Run a specific test
uv run pytest shouldigetaheatpump/tests/test_get_data.py::test_get_weather_data

# Run with coverage
uv run pytest --cov=shouldigetaheatpump --cov-report=html
```

#### Integration Tests

Integration tests use Selenium to test the full app in a browser.

**Requirements:**
- ChromeDriver must be installed and in your PATH
- Install with Homebrew: `brew install chromedriver`
- Or download from [ChromeDriver downloads](https://chromedriver.chromium.org/downloads)

**Running integration tests:**
```bash
uv run pytest -m integration
```

**Note:** Integration tests run automatically in CI (GitHub Actions has ChromeDriver pre-installed). They're optional for local development.

### Code Quality

```bash
# Format code
uv run ruff format shouldigetaheatpump/

# Lint code
uv run ruff check shouldigetaheatpump/
```

# TODO:

- Get historical weather data, using tomorrow.io
- Get heat pump cop numbers, maybe do linear regression

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

1. Enter a location by either:
   - Typing latitude and longitude coordinates (e.g., `51.1149, -114.0675`)
   - Clicking on the interactive map
2. View historical temperature data and heat pump efficiency analysis

## Development

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest shouldigetaheatpump/tests/test_get_data.py::test_get_weather_data

# Format code
uv run ruff format shouldigetaheatpump/

# Lint code
uv run ruff check shouldigetaheatpump/
```

# TODO:

- Get historical weather data, using tomorrow.io
- Get heat pump cop numbers, maybe do linear regression

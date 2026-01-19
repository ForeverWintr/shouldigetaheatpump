# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python web application that helps users determine whether installing a heat pump would be beneficial based on historical weather data and heat pump efficiency metrics (COP - Coefficient of Performance). Built with Dash/Plotly for visualization.

## Build and Development Commands

```bash
# Install dependencies
uv sync

# Run the Dash web app (available at http://127.0.0.1:8050/)
uv run python -m shouldigetaheatpump.dash_app

# Run all tests
uv run pytest

# Run a single test
uv run pytest shouldigetaheatpump/tests/test_get_data.py::test_get_weather_data

# Format code
uv run ruff format shouldigetaheatpump/

# Lint code
uv run ruff check shouldigetaheatpump/
```

## Architecture

**Data flow:** Weather API → Data parsing → DataFrame processing → Dash visualization

### Module Responsibilities

- **`get_data.py`** - Data retrieval and parsing: weather data from Open-Meteo API, heat pump specs (Daikin SkyAir 3-ton hardcoded), utility data from CSV
- **`conversions.py`** - Unit conversions via Pint, COP (Coefficient of Performance) calculations
- **`dash_app.py`** - Interactive web dashboard with Plotly graphs showing temperature data

### Key Patterns

- **API caching**: Weather API responses cached indefinitely in SQLite (`shouldigetaheatpump/requests-cache.sqlite`) to minimize API calls
- **Lazy singleton**: Pint UnitRegistry in `conversions.py` initialized once via `get_unit_registry()`
- **Data file paths**: Relative to module location using `Path(__file__).parent`

## Tech Stack

- Python 3.12+, uv for dependency management
- Dash 2.17 (Flask + Plotly) for web UI
- Pandas for data manipulation
- Pendulum for datetime handling
- Pint for unit conversions
- Open-Meteo API for historical weather data (no auth required)

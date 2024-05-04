from pathlib import Path
from pendulum import Date
import openmeteo_requests
import requests_cache
from loguru import logger
import pandas as pd


def get_weather_data(lat: float, lon: float, start: Date, end: Date):
    """Get historical weather data."""

    # Based on example code here: https://open-meteo.com/en/docs/historical-weather-api
    cache_path = Path(__file__).parent / "requests-cache"
    cache_session = requests_cache.CachedSession(cache_path, expire_after=-1)

    client = openmeteo_requests.Client(session=cache_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 51.11488758418279,
        "longitude": -114.06747997399614,
        "start_date": str(start),
        "end_date": str(end),
        "hourly": "temperature_2m",
    }
    [response] = client.weather_api(url, params=params)

    logger.info(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    logger.info(f"Elevation {response.Elevation()} m asl")

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    hourly_data["temperature_2m"] = hourly_temperature_2m

    return pd.DataFrame(data=hourly_data)

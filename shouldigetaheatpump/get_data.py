from pathlib import Path
import pendulum
import openmeteo_requests
import requests_cache
from loguru import logger
import pandas as pd


def get_weather_data(
    lat: float, long: float, start: pendulum.DateTime, end: pendulum.DateTime
):
    """Get historical weather data."""
    # Based on example code here: https://open-meteo.com/en/docs/historical-weather-api
    cache_path = Path(__file__).parent / "requests-cache"
    cache_session = requests_cache.CachedSession(cache_path, expire_after=-1)

    client = openmeteo_requests.Client(session=cache_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": str(start.in_tz("UTC").date()),
        "end_date": str(end.in_tz("UTC").date()),
        "hourly": "temperature_2m",
        "timezone": "auto",
    }
    [response] = client.weather_api(url, params=params)

    logger.info(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    logger.info(f"Elevation {response.Elevation()} m asl")

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=False),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=False),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            tz=response.Timezone().decode(),
            inclusive="left",
        )
    }
    hourly_data["temperature"] = hourly_temperature_2m

    result = pd.DataFrame(data=hourly_data)
    return result

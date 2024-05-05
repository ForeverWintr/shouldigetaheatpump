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


def parse_daikin_cop():
    """Skyair 3-ton, FTQ36/RZQ36"""
    header = "C FDB Btu/h kwh kw".split() + ["cop"]
    raw = """15.6 60.00 41,800 12.2 3.18 3.84
13.9 57.00 41,800 12.2 3.27 3.73
12.2 54.00 41,800 12.2 3.37 3.62
10.6 51.00 41,800 12.2 3.48 3.51
8.3 47.00 41,800 12.2 3.64 3.35
6.7 44.00 41,800 12.2 3.77 3.24
3.9 39.00 41,800 12.2 3.96 3.08
1.7 35.00 41,800 12.2 4.17 2.93
-1.1 30.00 41,800 12.2 4.40 2.77
-3.3 26.00 41,800 12.2 4.66 2.62
-5.6 22.00 41,800 12.2 4.95 2.46
-7.2 19.00 41,800 12.2 5.11 2.39
-8.3 17.00 41,800 12.2 5.33 2.29
-9.4 15.00 41,800 12.2 5.46 2.23
-10.6 13.00 41,800 12.2 5.66 2.16
-12.5 9.50 41,800 12.2 6.03 2.02
-14.7 5.50 41,800 12.2 6.46 1.89
-18.8 -1.84 41,500 12.2 7.47 1.63
-19.8 -3.64 40,300 11.8 7.40 1.59"""
    rows = raw.strip().split("\n")
    parsed_rows = []
    for row in rows:
        cells = row.split()
        parsed_rows.append([float(c.replace(",", "")) for c in cells])
    return pd.DataFrame.from_records(parsed_rows, columns=header)

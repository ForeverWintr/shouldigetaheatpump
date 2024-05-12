import itertools
from pathlib import Path
import pendulum
import openmeteo_requests
import requests_cache
from loguru import logger
import pandas as pd

from shouldigetaheatpump import conversions


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


def parse_daikin_data():
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


def parse_daikin_extended_data():

    raw = """
-13 -13 29.3 7.06 27.1 6.41 25.5 5.94 24.4 5.64 23.3 5.34 21.7 4.90
-9 -9 34.3 7.07 33 6.79 32.1 6.59 31.3 6.43 29.9 6.07 27.8 5.53
-3.64 -4 40.4 7.09 40.4 7.27 40.3 7.4 40 7.42 38.2 6.97 35.5 6.32
-1.84 -2.2 41.7 7.17 41.6 7.34 41.5 7.47 40 7.11 38.2 6.69 35.5 6.06
5.5 5 46.6 7.43 44.5 7.03 41.8 6.46 40 6.09 38.2 5.74 35.5 5.22
9.5 8.5 48 7.28 44.5 6.56 41.8 6.03 40 5.7 38.2 5.37 35.5 4.88
13 12 48 6.81 44.5 6.14 41.8 5.66 40 5.34 38.2 5.04 35.5 4.59
15 14 48 6.57 44.5 5.93 41.8 5.46 40 5.16 38.2 4.87 35.5 4.44
17 15.5 48 6.4 44.5 5.78 41.8 5.33 40 5.03 38.2 4.75 35.5 4.33
19 18 48 6.14 44.5 5.54 41.8 5.11 40 4.83 38.2 4.56 35.5 4.16
22 20 48 5.94 44.5 5.36 41.8 4.95 40 4.68 38.2 4.42 35.5 4.04
26 24 48 5.58 44.5 5.04 41.8 4.66 40 4.41 38.2 4.17 35.5 3.81
30 28 48 5.26 44.5 4.76 41.8 4.4 40 4.17 38.2 3.94 35.5 3.61
35 32 48 4.97 44.5 4.51 41.8 4.17 40 3.95 38.2 3.74 35.5 3.42
39 36 48 4.71 44.5 4.28 41.8 3.96 40 3.75 38.2 3.55 35.5 3.26
44 40 48 4.48 44.5 4.07 41.8 3.77 40 3.58 38.2 3.39 35.5 3.11
47 43 48 4.32 44.5 3.93 41.8 3.64 40 3.46 38.2 3.27 35.5 3.01
51 47 48 4.13 44.5 3.76 41.8 3.48 40 3.31 38.2 3.14 35.5 2.88
54 50 48 3.99 44.5 3.64 41.8 3.37 40 3.2 38.2 3.04 35.5 2.79
57 53 – – 44.5 3.52 41.8 3.27 40 3.11 38.2 2.95 35.5 2.71
60 56 – – 44.5 3.42 41.8 3.18 40 3.02 38.2 2.86 35.5 2.64
64 60 – – – – – – 40 2.9 38.2 2.76 35.5 2.54"""
    rows = raw.strip().split("\n")
    indoor_temps = [61, 65, 68, 70, 72, 75]
    # convert to metric
    ureg = conversions.get_unit_registry()
    indoor_temps = [
        int(ureg.Quantity(x, ureg.degF).to(ureg.degC).magnitude + 0.5)
        for x in indoor_temps
    ]

    # Total capacity, Milli-BTU-hour
    # Power Input, KW
    units = ["TC MBH", "PI KW"]

    # DB: dry bulb, WB: Wet bulb
    dry_bulbs = ["FDB", "FWB"]
    header = dry_bulbs + list(itertools.product(indoor_temps, units))

    parsed_rows = []
    for row in rows:
        cells = row.split()
        parsed_rows.append([float(c) if c != "–" else float("nan") for c in cells])

    df = pd.DataFrame.from_records(parsed_rows, columns=header)

    for colname in dry_bulbs:
        metric = ureg.Quantity(df[colname].values, ureg.degF).to(ureg.degC)
        metric_name = colname.replace("F", "C")
        df[metric_name] = metric

    return df


def parse_camrose_gj() -> pd.DataFrame:
    header = [
        "Invoice Date",
        "Opening Balance ($)",
        "Energy (GJ)",
        "Energy ($)",
        "Regulated ($)",
        "Other ($)",
        "GST ($)",
        "Payment & Transfers ($)",
        "Rebate ($)",
        "Balance ($)",
    ]
    dates = """
Apr 23, 2024
Mar 21, 2024
Feb 22, 2024
Jan 23, 2024
Dec 21, 2023
Nov 23, 2023
Oct 24, 2023
Sep 22, 2023
Aug 23, 2023
Jul 24, 2023
Jun 22, 2023
May 24, 2023
Apr 24, 2023"""
    raw = """
$122.38 7
$128.41 9
$124.03 9
$118.40 9
$105.56 8
$74.73 7
$47.39 4
$45.00 1
$56.06 1
$48.26 2
$63.13 1
$94.35 3
$153.89 6
$20.57 $76.12 $6.80
$25.79 $83.87 $6.87
$31.61 $83.83 $6.84
$30.64 $80.66 $6.80
$29.74 $76.13 $6.87
$25.82 $67.85 $6.84
$13.93 $50.41 $6.81
$3.84 $34.88 $6.39
$3.52 $32.93 $6.39
$7.32 $39.69 $6.36
$3.70 $35.84 $6.40
$10.47 $43.24 $6.39
$24.80 $58.68 $6.36
$5.20 -$122.38
$5.85 -$128.41
$6.13 -$124.03
$5.93 -$118.40
$5.66 -$105.56
$5.05 -$74.73
$3.58 -$47.39
$2.28 -$45.00
$2.16 -$56.06
$2.69 -$48.26
$2.32 -$63.13
$3.03 -$94.35
$4.51 -$153.89
$0.00 $108.69
$0.00 $122.38
$0.00 $128.41
$0.00 $124.03
$0.00 $118.40
$0.00 $105.56
$0.00 $74.73
$0.00 $47.39
$0.00 $45.00
$0.00 $56.06
$0.00 $48.26
$0.00 $63.13
$0.00 $94.35"""
    asdf

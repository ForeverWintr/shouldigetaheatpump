from pendulum import Date


def get_weather_data(lat: float, lon: float, start: Date, end: Date):
    """Get historical weather data"""

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 51.11488758418279,
        "longitude": -114.06747997399614,
        "start_date": "2024-04-18",
        "end_date": "2024-05-02",
        "hourly": "temperature_2m",
    }

    asdf

import pendulum

from shouldigetaheatpump import get_data


def test_get_weather_data():
    data = get_data.get_weather_data(
        lat=51.11516647256088,
        long=-114.06747997399614,
        start=pendulum.datetime(2024, 1, 1),
        end=pendulum.datetime(2024, 1, 2),
    )
    assert data.shape

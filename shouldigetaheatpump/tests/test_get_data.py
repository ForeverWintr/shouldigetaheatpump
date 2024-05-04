import pendulum

from shouldigetaheatpump import get_data


def test_get_weather_data():

    get_data.get_weather_data(
        lat=51.11516647256088,
        lon=-114.06747997399614,
        start=pendulum.date(2024, 1, 1),
        end=pendulum.date(2024, 1, 31),
    )
    assert 0

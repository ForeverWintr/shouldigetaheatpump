import pendulum
import pytest

from shouldigetaheatpump import get_data, conversions


def test_get_weather_data():
    data = get_data.get_weather_data(
        lat=51.11516647256088,
        long=-114.06747997399614,
        start=pendulum.datetime(2024, 1, 1),
        end=pendulum.datetime(2024, 1, 2),
    )
    assert data.shape


def test_parse_daikin_cop():

    parsed_cop = get_data.parse_daikin_data()
    parsed_extended = get_data.parse_daikin_extended_data()

    ureg = conversions.get_unit_registry()

    # index by dry bulb celcius temp.

    cop = conversions.calculate_cop(
        parsed_cop,
        heat_col="Btu/h",
        heat_unit=ureg.BTU / ureg.hour,
        energy_col="kw",
        energy_unit=ureg.kilowatt,
    )

    # This is using 68F, or 20C
    extended_cop = conversions.calculate_cop(
        parsed_extended.set_index("FDB"),
        heat_col=("68", "TC MBH"),
        heat_unit=1000 * ureg.BTU / ureg.hour,
        energy_col=("68", "PI KW"),
        energy_unit=ureg.kilowatt,
    )

    assert parsed_cop["cop"].tolist() == pytest.approx(cop.tolist(), rel=1e-2)

    btu = 41800 * ureg.BTU
    btuh = btu / ureg.hour
    kw_produced = btuh.to(ureg.kilowatt)

    kwh = 12.2 * ureg.kilowatt / ureg.hour
    kw = 3.18 * ureg.kilowatt

    cop = kw_produced / kw

    asdf

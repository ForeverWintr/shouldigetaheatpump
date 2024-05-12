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

    cop = conversions.calculate_cop(
        parsed_cop,
        heat_col="Btu/h",
        heat_unit=ureg.BTU / ureg.hour,
        energy_col="kw",
        energy_unit=ureg.kilowatt,
    )

    # This is using 68F, or 20C
    extended_cop = conversions.calculate_cop(
        parsed_extended,
        heat_col=(20, "TC MBH"),
        heat_unit=1000 * ureg.BTU / ureg.hour,
        energy_col=(20, "PI KW"),
        energy_unit=ureg.kilowatt,
    )
    parsed_extended["COP"] = extended_cop

    assert parsed_cop["cop"].tolist() == pytest.approx(cop.tolist(), rel=1e-2)

    # This value corresponds to -1.11C.
    assert extended_cop.iloc[12] == pytest.approx(cop.iloc[8])


def test_parse_camrose_gj() -> None:
    r = get_data.parse_camrose_gj()
    assert 0

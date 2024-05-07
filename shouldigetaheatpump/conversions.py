import pint
import pandas as pd

_UREG = None


def get_unit_registry() -> pint.UnitRegistry:
    global _UREG
    if not _UREG:
        _UREG = pint.UnitRegistry()
    return _UREG


def calculate_cop(
    data: pd.DataFrame,
    heat_col: str,
    heat_unit: pint.Unit,
    energy_col: str,
    energy_unit: pint.Unit,
):
    ureg = get_unit_registry()
    heat = ureg.Quantity(data[heat_col].values, heat_unit)
    energy = ureg.Quantity(data[energy_col].values, energy_unit)

    cop = heat.to(energy_unit) / energy

    return pd.Series(cop.magnitude, index=data.index.copy())

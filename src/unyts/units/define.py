#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.0'
__release__ = 20230118
__all__ = ['units']

from ..dictionaries import dictionary as _dictionary
from .custom import UserUnits, OtherUnits
from .force import Pressure, Weight, Compressibility
from .geometry import Length, Area, Volume
from .temperature import Temperature, TemperatureGradient
from .time import Time
from .unitless import Dimensionless, Percentage
from .ratios import Density, VolumeRatio, ProductivityIndex, PressureGradient
from .rates import Rate, Speed, Velocity
from .energy import Energy, Power
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str as unit_or_str, numeric as numeric


def units(value: numeric, unit: unit_or_str = None) -> Unit:
    """
    return an instance of units with the provided value and units.

    Parameters
    ----------
    value : int, float, numeric array, Series or DataFrame
        the value to assign the units.
    unit : str, optional
        the units to assign the value. The default is None.

    Raises
    ------
    TypeError
        if value or units are not the appropriate kind.

    Returns
    -------
    units
        instance of units.

    """
    if unit is None and '.units.' in str(type(value)):
        value, unit = value.value, value.units
    if unit is None:
        unit = 'Dimensionless'
    if type(unit) is not str:
        raise TypeError("'units' must be a string.")
    if not isinstance(value, numeric):
        raise TypeError("'value' parameter must be numeric.")

    unit = unit.strip()
    for kind in _dictionary:
        if unit in _dictionary[kind]:
            u = eval(kind + "(0, '" + unit + "')")
            if type(u) is Percentage:
                u.value = value / 100
            else:
                u.value = value
            return u

    return UserUnits(value, unit)

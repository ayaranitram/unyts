#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.7'
__release__ = 20221229
__all__ = ['units', 'numeric', 'array_like']

from ..dictionaries import dictionary
from .custom import userUnits, otherUnits
from .force import pressure, weight, compressibility
from .geometry import length, area, volume
from .temperature import temperature, temperatureGradient
from .time import time
from .unitless import dimensionless, percentage
from .ratios import density, volumeRatio, productivityIndex, pressureGradient
from .rates import rate, speed, velocity
from .energy import energy, power
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, array_like, number, numeric


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
        unit = 'dimensionless'
    if type(unit) is not str:
        raise TypeError("'units' must be a string.")

    unit = unit.strip()
    for kind in dictionary:
        if unit in dictionary[kind]:
            if isinstance(value, number):
                return eval(kind + "(" + str(value) + ",'" + unit + "')")
            elif isinstance(value, array_like):
                u = eval(kind + "(" + str(0) + ",'" + unit + "')")
                u.value = value
                return u
            else:
                raise TypeError("'value' parameter must be numeric.")

    return userUnits(value, unit)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['units']

from ..dictionaries import dictionary
from .custom import UserUnits, OtherUnits
from .force import Pressure, Weight, Compressibility
from .geometry import Length, Area, Volume
from .temperature import Temperature, TemperatureGradient
from .time import Time
from .unitless import Dimensionless, Percentage
from .ratios import Density, VolumeRatio, ProductivityIndex, PressureGradient
from .rates import Rate, Speed, Velocity
from .energy import Energy, Power

from numpy import ndarray
from numbers import Number

array_like = [ndarray]
try:
    from pandas import Series, DataFrame

    array_like += [Series, DataFrame]
except:
    pass
array_like = tuple(array_like)

from typing import Union

numeric = Union[int, float, complex] + array_like


def units(value, unit=None):
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

    unit = unit.strip()
    for kind in dictionary:
        if unit in dictionary[kind]:
            if isinstance(value, Number):
                return eval(kind + "(" + str(value) + ",'" + unit + "')")
            elif isinstance(value, array_like):
                u = eval(kind + "(" + str(0) + ",'" + unit + "')")
                u.value = value
                return u
            else:
                raise TypeError("'value' parameter must be numeric.")

    return UserUnits(value, unit)

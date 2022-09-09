#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.2.7'
__release__ = 20220908


from .._dictionaries import dictionary
from .custom import userUnits, otherUnits
from .force import pressure, weight, compressibility
from .geometry import length, area, volume
from .temperature import temperature, temperatureGradient
from .time import time
from .unitless import dimensionless, percentage
from .ratios import density, volumeRatio, productivityIndex, pressureGradient
from .rates import rate, speed, velocity
from .energy import energy, power

from numpy import ndarray
from numbers import Number

arraylike = [ndarray]
try:
    from pandas import Series, DataFrame
    arraylike += [Series, DataFrame]
except:
    pass
arraylike = tuple(arraylike)

def units(value, units=None):
    """
    return an instance of units with the provided value and units.

    Parameters
    ----------
    value : int, float, numeric array, Series or DataFrame
        the value to assign the units.
    units : str, optional
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
    if units is None and '.units.' in str(type(value)):
        value, units = value.value, value.units
    if units is None:
        units = 'dimensionless'
    if type(units) is not str:
        raise TypeError("'units' must be a string.")
    units = units.strip()
    for kind in dictionary:
        if units in dictionary[kind]:
            if isinstance(value, Number):
                return eval(kind + "(" + str(value) + ",'" + units + "')")
            elif isinstance(value, arraylike):
                u = eval(kind + "(" + str(0) + ",'" + units + "')")
                u.value = value
                return u
            else:
                raise TypeError("'value' parameter must be numeric.")
    return userUnits(value, units)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.1'
__release__ = 20220803

from .._dictionaries import dictionary
from .custom import userUnits
from .force import pressure, weight, compressibility
from .geometry import length, area, volume
from .temperature import temperature
from .time import time
from .unitless import dimensionless
from .ratios import density, volumeRatio
from .rates import rate, speed


def units(value, units=None):
    if units is None and '.units.' in str(type(value)):
        value, units = value.value, value.units
    if units is None:
        units = 'dimensionless'
    if type(units) is not str:
        raise TypeError("'units' must be a string.")
    units = units.strip()
    for kind in dictionary:
        if units in dictionary[kind]:
            return eval( kind + "(" + str(value) + ",'" + units + "')" )
    return userUnits(value, units)


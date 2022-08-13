#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.1'
__release__ = 20220803

from .._dictionaries import dictionary
from .._unit import _units


class length(_units):
    classUnits = dictionary['length']
    def __init__(self, value, units):
        self.name = 'length'
        self.kind = length
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class area(_units):
    classUnits = dictionary['area']
    def __init__(self, value, units):
        self.name = 'area'
        self.kind = area
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class volume(_units):
    classUnits = dictionary['volume']
    def __init__(self, value, units):
        self.name = 'volume'
        self.kind = volume
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
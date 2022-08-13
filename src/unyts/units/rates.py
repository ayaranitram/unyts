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


class rate(_units):
    classUnits = dictionary['rate']
    def __init__(self, value, units):
        self.name = 'rate'
        self.kind = rate
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class speed(_units):
    classUnits = dictionary['speed']
    def __init__(self, value, units):
        self.name = 'speed'
        self.kind = speed
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

def velocity(value, units):
    return speed(value, units)
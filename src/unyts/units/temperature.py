#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.2'
__release__ = 20220831

from .._dictionaries import dictionary
from .._unit import _units


class temperature(_units):
    classUnits = dictionary['temperature']
    def __init__(self, value, units):
        self.name = 'temperature'
        self.kind = temperature
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
        

class temperatureGradient(_units):
    classUnits = dictionary['temperatureGradient']
    def __init__(self, value, units):
        self.name = 'temperatureGradient'
        self.kind = temperatureGradient
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
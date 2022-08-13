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


class pressure(_units):
    classUnits = dictionary['pressure']
    def __init__(self, value, units):
        self.name = 'pressure'
        self.kind = pressure
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class weight(_units):
    classUnits = dictionary['weight']
    def __init__(self, value, units):
        self.name = 'weight'
        self.kind = weight
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class compressibility(_units):
    classUnits = dictionary['compressibility']
    def __init__(self, value, units):
        self.name = 'compressibility'
        self.kind = compressibility
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
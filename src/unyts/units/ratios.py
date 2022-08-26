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


class density(_units):
    classUnits = dictionary['density']
    def __init__(self, value, units):
        self.name = 'density'
        self.kind = density
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class volumeRatio(_units):
    classUnits = dictionary['volumeRatio']
    def __init__(self, value, units):
        self.name = 'volumeRatio'
        self.kid = volumeRatio
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class productivityIndex(_units):
    classUnits = dictionary['productivityIndex']
    def __init__(self, value, units) :
        self.name = 'productivityIndex'
        self.kind = productivityIndex
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class pressureGradient(_units):
    classUnits = dictionary['pressureGradient']
    def __init__(self, value, units) :
        self.name = 'pressureGradient'
        self.kind = pressureGradient
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


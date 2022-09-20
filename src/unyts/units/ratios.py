#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['density', 'volumeRatio', 'productivityIndex', 'pressureGradient']

from ..dictionaries import dictionary
from ..unit_class import unit


class density(unit):
    classUnits = dictionary['density']
    def __init__(self, value, units):
        self.name = 'density'
        self.kind = density
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class volumeRatio(unit):
    classUnits = dictionary['volumeRatio']
    def __init__(self, value, units):
        self.name = 'volumeRatio'
        self.kid = volumeRatio
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class productivityIndex(unit):
    classUnits = dictionary['productivityIndex']
    def __init__(self, value, units) :
        self.name = 'productivityIndex'
        self.kind = productivityIndex
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class pressureGradient(unit):
    classUnits = dictionary['pressureGradient']
    def __init__(self, value, units) :
        self.name = 'pressureGradient'
        self.kind = pressureGradient
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['pressure', 'weight', 'compressibility']

from ..dictionaries import dictionary
from ..unit_class import unit


class pressure(unit):
    classUnits = dictionary['pressure']
    def __init__(self, value, units):
        self.name = 'pressure'
        self.kind = pressure
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class weight(unit):
    classUnits = dictionary['weight']
    def __init__(self, value, units):
        self.name = 'weight'
        self.kind = weight
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class compressibility(unit):
    classUnits = dictionary['compressibility']
    def __init__(self, value, units):
        self.name = 'compressibility'
        self.kind = compressibility
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
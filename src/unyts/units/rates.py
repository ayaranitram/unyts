#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['rate', 'speed', 'velocity']

from ..dictionaries import dictionary
from ..unit_class import unit


class rate(unit):
    classUnits = dictionary['rate']
    def __init__(self, value, units):
        self.name = 'rate'
        self.kind = rate
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class speed(unit):
    classUnits = dictionary['speed']
    def __init__(self, value, units):
        self.name = 'speed'
        self.kind = speed
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


def velocity(value, units):
    return speed(value, units)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['length', 'area', 'volume']

from ..dictionaries import dictionary
from ..unit_class import Unit


class length(Unit):
    classUnits = dictionary['length']

    def __init__(self, value, units):
        self.name = 'length'
        self.kind = length
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class area(Unit):
    classUnits = dictionary['area']

    def __init__(self, value, units):
        self.name = 'area'
        self.kind = area
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class volume(Unit):
    classUnits = dictionary['volume']

    def __init__(self, value, units):
        self.name = 'volume'
        self.kind = volume
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

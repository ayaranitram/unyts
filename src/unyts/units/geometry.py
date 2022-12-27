#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['Length', 'Area', 'Volume']

from ..dictionaries import dictionary
from ..unit_class import Unit


class Length(Unit):
    classUnits = dictionary['Length']

    def __init__(self, value, units):
        self.name = 'Length'
        self.kind = Length
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Area(Unit):
    classUnits = dictionary['Area']

    def __init__(self, value, units):
        self.name = 'Area'
        self.kind = Area
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Volume(Unit):
    classUnits = dictionary['Volume']

    def __init__(self, value, units):
        self.name = 'Volume'
        self.kind = Volume
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

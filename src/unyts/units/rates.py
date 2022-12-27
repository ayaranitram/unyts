#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['Rate', 'Speed', 'Velocity']

from ..dictionaries import dictionary
from ..unit_class import Unit


class Rate(Unit):
    classUnits = dictionary['Rate']

    def __init__(self, value, units):
        self.name = 'Rate'
        self.kind = Rate
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Speed(Unit):
    classUnits = dictionary['Speed']

    def __init__(self, value, units):
        self.name = 'Speed'
        self.kind = Speed
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


def Velocity(value, units):
    return Speed(value, units)

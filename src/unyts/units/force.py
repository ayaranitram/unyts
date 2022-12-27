#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['Pressure', 'Weight', 'Compressibility']

from ..dictionaries import dictionary
from ..unit_class import Unit


class Pressure(Unit):
    classUnits = dictionary['Pressure']

    def __init__(self, value, units):
        self.name = 'Pressure'
        self.kind = Pressure
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Weight(Unit):
    classUnits = dictionary['Weight']

    def __init__(self, value, units):
        self.name = 'Weight'
        self.kind = Weight
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Compressibility(Unit):
    classUnits = dictionary['Compressibility']

    def __init__(self, value, units):
        self.name = 'Compressibility'
        self.kind = Compressibility
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.4'
__release__ = 20230121
__all__ = ['Force', 'Pressure', 'Weight', 'Compressibility', 'Viscosity']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Force(Unit):
    classUnits = _dictionary['Force']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'force'
        self.kind = Force
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Pressure(Unit):
    classUnits = _dictionary['Pressure']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'pressure'
        self.kind = Pressure
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Weight(Unit):
    classUnits = _dictionary['Weight']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'weight'
        self.kind = Weight
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Compressibility(Unit):
    classUnits = _dictionary['Compressibility']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'compressibility'
        self.kind = Compressibility
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

class Viscosity(Unit):
    classUnits = _dictionary['Viscosity']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'viscosity'
        self.kind = Viscosity
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


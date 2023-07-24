#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Force', 'Pressure', 'Weight', 'Compressibility', 'Viscosity']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Force(Unit):
    classUnits = _dictionary['Force']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'force' if name is None else name
        self.kind = Force
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Pressure(Unit):
    classUnits = _dictionary['Pressure']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'pressure' if name is None else name
        self.kind = Pressure
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Weight(Unit):
    classUnits = _dictionary['Weight']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'weight' if name is None else name
        self.kind = Weight
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Compressibility(Unit):
    classUnits = _dictionary['Compressibility']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'compressibility' if name is None else name
        self.kind = Compressibility
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Viscosity(Unit):
    classUnits = _dictionary['Viscosity']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'viscosity' if name is None else name
        self.kind = Viscosity
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

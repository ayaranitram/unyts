#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.2'
__release__ = 20230107
__all__ = ['Pressure', 'Weight', 'Compressibility']

from unyts.dictionaries import dictionary
from unyts.unit_class import Unit
from unyts.helpers.common_classes import unit_or_str, numeric


class Pressure(Unit):
    classUnits = dictionary['Pressure']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'pressure'
        self.kind = Pressure
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Weight(Unit):
    classUnits = dictionary['Weight']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'weight'
        self.kind = Weight
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Compressibility(Unit):
    classUnits = dictionary['Compressibility']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'compressibility'
        self.kind = Compressibility
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

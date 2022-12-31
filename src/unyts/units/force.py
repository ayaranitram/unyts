#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['pressure', 'weight', 'compressibility']

from unyts.dictionaries import dictionary
from unyts.unit_class import Unit
from unyts.helpers.common_classes import unit_or_str, numeric


class pressure(Unit):
    classUnits = dictionary['pressure']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'pressure'
        self.kind = pressure
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class weight(Unit):
    classUnits = dictionary['weight']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'weight'
        self.kind = weight
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class compressibility(Unit):
    classUnits = dictionary['compressibility']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'compressibility'
        self.kind = compressibility
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

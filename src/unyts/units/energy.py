#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.3'
__release__ = 20230118
__all__ = ['Energy', 'Power']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Energy(Unit):
    classUnits = _dictionary['Energy']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'energy'
        self.kind = Energy
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Power(Unit):
    classUnits = _dictionary['Power']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'power'
        self.kind = Power
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Current(Unit):
    classUnits = _dictionary['Current']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'current'
        self.kind = Current
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Voltage(Unit):
    classUnits = _dictionary['Voltage']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'voltage'
        self.kind = Voltage
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

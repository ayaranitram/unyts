#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.4'
__release__ = 20230121
__all__ = ['Time', 'Frequency']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Time(Unit):
    classUnits = _dictionary['Time']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'time'
        self.kind = Time
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

    def __mul__(self, other):
        from .energy import Power
        if type(other) is Power:
            return super().__mul__(other).to('Wh')
        else:
            return super().__mul__(other)


class Frequency(Unit):
    classUnits = _dictionary['Frequency']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'frequency'
        self.kind = Frequency
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

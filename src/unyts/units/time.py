#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Time', 'Frequency']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Time(Unit):
    class_units = _dictionary['Time']
    __slots__ = ('unit', 'value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'time' if name is None else name
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
    class_units = _dictionary['Frequency']
    __slots__ = ('unit', 'value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'frequency' if name is None else name
        self.kind = Frequency
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

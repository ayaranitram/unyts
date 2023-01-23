#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.3'
__release__ = 20230118
__all__ = ['Rate', 'Speed', 'Velocity']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Rate(Unit):
    classUnits = _dictionary['Rate']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'rate'
        self.kind = Rate
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Velocity(Unit):
    classUnits = _dictionary['Velocity']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'velocity'
        self.kind = Velocity
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


def Speed(value: numeric, units: unit_or_str):
    return Velocity(value, units)

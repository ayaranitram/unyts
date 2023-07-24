#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Temperature', 'TemperatureGradient']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Temperature(Unit):
    classUnits = _dictionary['Temperature']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'temperature' if name is None else name
        self.kind = Temperature
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class TemperatureGradient(Unit):
    classUnits = _dictionary['TemperatureGradient']

    def __init__(self, value: str, units: unit_or_str, name=None):
        self.name = 'temperature_gradient' if name is None else name
        self.kind = TemperatureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

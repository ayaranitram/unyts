#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.7'
__release__ = 20221229
__all__ = ['temperature', 'temperatureGradient']

from ..dictionaries import dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class temperature(Unit):
    classUnits = dictionary['temperature']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'temperature'
        self.kind = temperature
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class temperatureGradient(Unit):
    classUnits = dictionary['temperatureGradient']

    def __init__(self, value: str, units: unit_or_str) -> Unit:
        self.name = 'temperatureGradient'
        self.kind = temperatureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

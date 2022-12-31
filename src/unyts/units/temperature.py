#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['Temperature', 'TemperatureGradient']

from unyts.dictionaries import dictionary
from unyts.unit_class import Unit
from unyts.helpers.common_classes import unit_or_str, numeric


class Temperature(Unit):
    classUnits = dictionary['Temperature']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'Temperature'
        self.kind = Temperature
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class TemperatureGradient(Unit):
    classUnits = dictionary['TemperatureGradient']

    def __init__(self, value: str, units: unit_or_str) -> Unit:
        self.name = 'TemperatureGradient'
        self.kind = TemperatureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

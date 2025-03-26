#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250320
__all__ = ['Temperature', 'TemperatureGradient']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Temperature(Unit):
    class_units = _dictionary['Temperature']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'temperature' if name is None else name
        super().__init__(value, units, name)
        self.kind = Temperature
        self.__unit = self.check_unit(units)


class TemperatureGradient(Unit):
    class_units = _dictionary['TemperatureGradient']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: str, units: unit_or_str, name=None):
        name = 'temperature_gradient' if name is None else name
        super().__init__(value, units, name)
        self.kind = TemperatureGradient
        self.__unit = self.check_unit(units)

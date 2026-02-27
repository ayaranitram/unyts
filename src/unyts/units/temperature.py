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
    """A class to represent a temperature quantity with a value, unit, and name, and to provide methods for checking valid units and converting between them."""
    class_units = _dictionary['Temperature']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Temperature object with a value and units."""
        name = 'temperature' if name is None else name
        super().__init__(value, units, name)
        self.kind = Temperature
        self.__unit = self.check_unit(units)


class TemperatureGradient(Unit):
    """A class to represent temperature gradient units."""
    class_units = _dictionary['TemperatureGradient']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a TemperatureGradient object with a value and units."""
        name = 'temperature_gradient' if name is None else name
        super().__init__(value, units, name)
        self.kind = TemperatureGradient
        self.__unit = self.check_unit(units)

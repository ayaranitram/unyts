#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250320
__all__ = ['Rate', 'Speed', 'Velocity', 'Acceleration']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Rate(Unit):
    """A class to represent a general rate, which is a quantity that describes how one variable changes with respect to another variable (e.g., time)."""
    class_units = _dictionary['Rate']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Rate object with a value and units."""
        name = 'rate' if name is None else name
        super().__init__(value, units, name)
        self.kind = Rate
        self.__unit = self.check_unit(units)


class Velocity(Unit):
    """A class to represent velocity quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Velocity']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Velocity object with a value and units."""
        name = 'velocity' if name is None else name
        super().__init__(value, units, name)
        self.kind = Velocity
        self.__unit = self.check_unit(units)


def Speed(value: numeric, units: unit_or_str, name=None):
    """Return a Velocity object with the given value and units."""
    return Velocity(value, units, name)


class Acceleration(Unit):
    """A class to represent acceleration quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Acceleration']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize an Acceleration object with a value and units."""
        name = 'acceleration' if name is None else name
        super().__init__(value, units, name)
        self.kind = Acceleration
        self.__unit = self.check_unit(units)

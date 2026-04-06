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


def _add_to_class_units(cls, units_str):
    """Add a validated unit string to cls.class_units and the dictionary."""
    dict_key = cls.__name__
    if isinstance(cls.class_units, tuple):
        cls.class_units = cls.class_units + (units_str,)
    else:
        cls.class_units = list(cls.class_units) + [units_str]
    _dictionary[dict_key] = cls.class_units


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

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 2:
            return False
        num, time = parts
        times = _dictionary.get('Time', ())
        if time not in times:
            return False
        if num in _dictionary.get('Volume', ()) or num in _dictionary.get('Weight', ()) or num in _dictionary.get('Data', ()):
            _add_to_class_units(cls, units)
            return True
        return False


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

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 2:
            return False
        length, time = parts
        if length in _dictionary.get('Length', ()) and time in _dictionary.get('Time', ()):
            _add_to_class_units(cls, units)
            return True
        return False


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

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        lengths = _dictionary.get('Length', ())
        times = _dictionary.get('Time', ())
        # Handle length/time2 format (e.g., m/s2)
        parts = units.split('/')
        if len(parts) == 2:
            length, time_part = parts
            if length in lengths and time_part.endswith('2') and time_part[:-1] in times:
                _add_to_class_units(cls, units)
                return True
        # Handle length/time/time format (e.g., m/s/s)
        if len(parts) == 3:
            length, t1, t2 = parts
            if length in lengths and t1 in times and t2 in times:
                _add_to_class_units(cls, units)
                return True
        return False

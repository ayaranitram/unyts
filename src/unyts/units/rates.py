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
    class_units = _dictionary['Rate']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'rate' if name is None else name
        super().__init__(value, units, name)
        self.kind = Rate
        self.__unit = self.check_unit(units)


class Velocity(Unit):
    class_units = _dictionary['Velocity']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'velocity' if name is None else name
        super().__init__(value, units, name)
        self.kind = Velocity
        self.__unit = self.check_unit(units)


def Speed(value: numeric, units: unit_or_str, name=None):
    return Velocity(value, units, name)


class Acceleration(Unit):
    class_units = _dictionary['Acceleration']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'acceleration' if name is None else name
        super().__init__(value, units, name)
        self.kind = Acceleration
        self.__unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250320
__all__ = ['Dimensionless', 'Percentage', 'unitless_names']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..errors import WrongUnitsError
from ..helpers.common_classes import unit_or_str, numeric
from ..dictionaries import unitless_names


class Dimensionless(Unit):
    class_units = _dictionary['Dimensionless']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str = None, name=None):
        name = 'dimensionless' if name is None else name
        super().__init__(value, units, name)
        self.kind = Dimensionless
        if units is None:
            units = 'dimensionless'
        self.__unit = self.check_unit(units)

    def convert(self, new_unit: unit_or_str = None) -> Unit:
        if new_unit is not None and type(new_unit) is not str:
            try:
                new_unit = new_unit.unit
            except:
                raise WrongUnitsError("'" + str(new_unit) + "' for '" + str(type(self)) + "'")
        if new_unit is None or len(new_unit) == 0:
            return self.value
        elif new_unit in _dictionary['Percentage']:
            return Percentage(self.value * 100, new_unit)
        elif new_unit in _dictionary['Dimensionless']:
            return Dimensionless(self.value, new_unit)
        else:
            from .define import units
            return units(self.value, new_unit)

    def to(self, new_unit: unit_or_str = None) -> Unit:
        return self.convert(new_unit)


class Percentage(Dimensionless):
    class_units = _dictionary['Percentage']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str = None, name=None):
        name = 'percentage' if name is None else name
        super().__init__(0, None, name)
        self.kind = Percentage
        self.value = self.check_value(value) / 100
        if units is None:
            units = 'percent'
        self.unit = self.check_unit(units)

    def __repr__(self) -> str:
        return f"{self.value * 100}_{self.unit}"

    def __str__(self) -> str:
        return f"{self.value * 100}_{self.unit}"

    def __neg__(self) -> Unit:
        return self.kind(self.value * -100, self.unit)

    def __abs__(self) -> Unit:
        return self.kind(abs(self.value) * 100, self.unit)

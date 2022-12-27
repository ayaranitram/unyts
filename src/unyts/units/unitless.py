#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['dimensionless', 'percentage']

from ..dictionaries import dictionary
from ..unit_class import Unit
from ..errors import WrongUnitsError


class dimensionless(Unit):
    classUnits = dictionary['dimensionless']

    def __init__(self, value, units=None):
        self.name = 'dimensionless'
        self.kind = dimensionless
        self.value = self.check_value(value)
        if units is None:
            units = 'dimensionless'
        self.unit = self.check_unit(units)

    def convert(self, new_unit=None):
        if new_unit is not None and type(new_unit) is not str:
            try:
                new_unit = new_unit.unit
            except:
                raise WrongUnitsError("'" + str(new_unit) + "' for '" + str(self.name) + "'")
        if new_unit is None or len(new_unit) == 0:
            return self.value
        elif new_unit in dictionary['percentage']:
            return percentage(self.value * 100, new_unit)
        elif new_unit in dictionary['dimensionless']:
            return dimensionless(self.value, new_unit)
        else:
            from .define import units
            return units(self.value, new_unit)

    def to(self, new_unit=None):
        return self.convert(new_unit)


class percentage(dimensionless):
    classUnits = dictionary['percentage']

    def __init__(self, value, units=None):
        self.name = 'percentage'
        self.kind = percentage
        self.value = self.check_value(value) / 100
        if units is None:
            units = 'percentage'
        self.unit = self.check_unit(units)

    def __repr__(self):
        return str(self.value * 100) + '_' + str(self.unit)

    def __str__(self):
        return str(self.value * 100) + '_' + str(self.unit)

    def __neg__(self):
        return self.kind(self.value * -100, self.unit)

    def __abs__(self):
        return self.kind(abs(self.value) * 100, self.unit)

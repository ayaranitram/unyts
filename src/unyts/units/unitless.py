#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220820
__all__ = ['dimensionless', 'percentage']

from ..dictionaries import dictionary
from ..unit_class import unit
from ..errors import WrongUnitsError


class dimensionless(unit):
    classUnits = dictionary['dimensionless']
    def __init__(self, value, units=None):
        self.name = 'dimensionless'
        self.kind = dimensionless
        self.value = self.checkValue(value)
        if units is None:
            units = 'dimensionless'
        self.unit = self.checkUnit(units)

    def convert(self, newunit=None):
        if newunit is not None and type(newunit) is not str:
            try:
                newunit = newunit.unit
            except:
                raise WrongUnitsError("'" + str(newunit) + "' for '" + str(self.name) + "'")
        if newunit is None or len(newunit) == 0:
            return self.value
        elif newunit in dictionary['percentage']:
            return percentage(self.value * 100, newunit)
        elif newunit in dictionary['dimensionless']:
            return dimensionless(self.value, newunit)
        else:
            from .define import units
            return units(self.value, newunit)

    def to(self, newunit=None):
        return self.convert(newunit)


class percentage(dimensionless):
    classUnits = dictionary['percentage']
    def __init__(self, value, units=None):
        self.name = 'percentage'
        self.kind = percentage
        self.value = self.checkValue(value) / 100
        if units is None:
            units = 'percentage'
        self.unit = self.checkUnit(units)

    def __repr__(self):
        return str(self.value * 100) + '_' + str(self.unit)

    def __str__(self) :
        return str(self.value * 100) + '_' + str(self.unit)

    def __neg__(self):
        return self.kind(self.value * -100, self.unit)

    def __abs__(self):
        return self.kind(abs(self.value) * 100, self.unit)
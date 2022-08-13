#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.1'
__release__ = 20220803

from .._dictionaries import dictionary
from .._unit import _units


class dimensionless(_units):
    classUnits = dictionary['dimensionless']
    def __init__(self, value, units=None):
        self.name = 'dimensionless'
        self.kind = dimensionless
        self.value = self.checkValue(value)
        if units is None :
            units = 'dimensionless'
        self.unit = self.checkUnit(units)
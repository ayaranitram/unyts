#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.1'
__release__ = 20220803

from .._dictionaries import dictionary
from .._unit import _units


class energy(_units):
    classUnits = dictionary['energy']
    def __init__(self, value, units):
        self.name = 'energy'
        self.kind = energy
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class power(_units):
    classUnits = dictionary['power']
    def __init__(self, value, units):
        self.name = 'power'
        self.kind = power
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

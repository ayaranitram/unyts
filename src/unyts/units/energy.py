#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['energy', 'power']

from ..dictionaries import dictionary
from ..unit_class import unit


class energy(unit):
    classUnits = dictionary['energy']
    def __init__(self, value, units):
        self.name = 'energy'
        self.kind = energy
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)


class power(unit):
    classUnits = dictionary['power']
    def __init__(self, value, units):
        self.name = 'power'
        self.kind = power
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
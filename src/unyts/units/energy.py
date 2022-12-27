#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['Energy', 'Power']

from ..dictionaries import dictionary
from ..unit_class import Unit


class Energy(Unit):
    classUnits = dictionary['Energy']

    def __init__(self, value, unit):
        self.name = 'Energy'
        self.kind = Energy
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Power(Unit):
    classUnits = dictionary['Power']

    def __init__(self, value, unit):
        self.name = 'Power'
        self.kind = Power
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

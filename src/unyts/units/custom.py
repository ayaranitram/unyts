#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.2'
__release__ = 20220908
__all__ = ['customUnits', 'userUnits', 'otherUnits']

from .._dictionaries import dictionary
from .._unit import _units


def customUnits(value, units):
    return userUnits(value, units)

def otherUnits(value, units):
    return userUnits(value, units)

class userUnits(_units):
    classUnits = dictionary['userUnits']
    def __init__(self, value, units):
        self.name = 'userUnits'
        self.kind = userUnits
        units = units.strip()
        if units not in dictionary['userUnits']:
            dictionary['userUnits'].append(units)
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['customUnits', 'userUnits', 'otherUnits']

from ..dictionaries import dictionary
from ..unit_class import Unit


def customUnits(value, units):
    return userUnits(value, units)


def otherUnits(value, units):
    return userUnits(value, units)


class userUnits(Unit):
    classUnits = dictionary['userUnits']

    def __init__(self, value, units):
        self.name = 'userUnits'
        self.kind = userUnits
        units = units.strip()
        if units not in dictionary['userUnits']:
            dictionary['userUnits'].append(units)
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['CustomUnits', 'UserUnits', 'OtherUnits']

from ..dictionaries import dictionary
from ..unit_class import Unit


def CustomUnits(value, units):
    return UserUnits(value, units)


def OtherUnits(value, units):
    return UserUnits(value, units)


class UserUnits(Unit):
    classUnits = dictionary['UserUnits']

    def __init__(self, value, units):
        self.name = 'UserUnits'
        self.kind = UserUnits
        units = units.strip()
        if units not in dictionary['UserUnits']:
            dictionary['UserUnits'].append(units)
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['time']

from ..dictionaries import dictionary
from ..unit_class import Unit


class time(Unit):
    classUnits = dictionary['time']

    def __init__(self, value, units):
        self.name = 'time'
        self.kind = time
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

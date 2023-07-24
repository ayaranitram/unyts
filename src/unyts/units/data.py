#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 00:23:43 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Data']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Data(Unit):
    classUnits = _dictionary['Data']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'data' if name is None else name
        self.kind = Data
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

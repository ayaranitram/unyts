#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 23:34:59 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Mass']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Mass(Unit):
    class_units = _dictionary['Mass']
    __slots__ = ('unit', 'value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'mass' if name is None else name
        self.kind = Mass
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

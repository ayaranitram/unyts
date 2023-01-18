#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.3'
__release__ = 20230118
__all__ = ['Time']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Time(Unit):
    classUnits = _dictionary['Time']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'time'
        self.kind = Time
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

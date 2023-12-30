#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 21:45:34 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Date']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from .time import Time
from ..helpers.common_classes import unit_or_str, numeric
from numpy import datetime64, timedelta64


class Date(Unit):
    class_units = _dictionary['Date']

    def __init__(self, value, units='date', name=None):
        self.value = datetime64(value)
        self.name = 'date' if name is None else name
        self.kind = Date

    def __add__(self, other):
        if isinstance(other, Time):
            return Date(self.value + timedelta64(other.value, other.unit))

    def __sub__(self, other):
        if isinstance(other, Time):
            return Date(self.value - timedelta64(other.value, other.unit))

    def year(self):
        return self.value.astype(object).year

    def month(self):
        return self.value.astype(object).month

    def day(self):
        return self.value.astype(object).day

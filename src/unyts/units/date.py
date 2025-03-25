#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 21:45:34 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250323
__all__ = ['Date']

from ..dictionaries import dictionary as _dictionary
from ..errors import WrongDateFormatError
from ..unit_class import Unit
from .time import Time
from ..helpers.common_classes import unit_or_str, numeric
from numpy import datetime64, timedelta64


class Date(Unit):
    class_units = _dictionary['Date']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value, units='date', name=None):
        name = 'date' if name is None else name
        super().__init__(0, None, name)
        self.kind = Date
        self.value = self.check_date(value)
        self.unit = 'date'

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value):
        self.__value = self.check_date(value)

    @property
    def values(self):
        return self.__value
    @values.setter
    def value(self, value):
        self.__value = self.check_date(value)

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

    def check_date(self, value):
        try:
            return datetime64(value)
        except Exception as e:
            raise WrongDateFormatError(repr(e))
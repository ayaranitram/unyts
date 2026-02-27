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
    """A class to represent a date value with associated unit and name, supporting addition and subtraction with Time objects and extraction of year, month, and day components."""
    class_units = _dictionary['Date']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value, units='date', name=None):
        """Initialize a Date object."""
        name = 'date' if name is None else name
        super().__init__(0, None, name)
        self.kind = Date
        self.value = self.check_date(value)
        self.unit = 'date'

    @property
    def value(self):
        """Return the value of the Date object."""
        return self.__value
    @value.setter
    def value(self, value):
        """Validate and set the value of the Date object."""
        self.__value = self.check_date(value)

    @property
    def values(self):
        """Return the values of the Date object."""
        return self.__value
    @values.setter
    def values(self, value):
        """Validate and set the values of the Date object."""
        self.__value = self.check_date(value)

    def __add__(self, other):
        """Add a Time object to the Date object."""
        if isinstance(other, Time):
            return Date(self.value + timedelta64(other.value, other.unit))

    def __sub__(self, other):
        """Subtract a Time object from the Date object."""
        if isinstance(other, Time):
            return Date(self.value - timedelta64(other.value, other.unit))

    def year(self):
        """Return the year component of the Date object."""
        return self.value.astype(object).year

    def month(self):
        """Return the month component of the Date object."""
        return self.value.astype(object).month

    def day(self):
        """Return the day component of the Date object."""
        return self.value.astype(object).day

    def check_date(self, value):
        """Validate and return a numpy datetime64 object from a given value."""
        try:
            return datetime64(value)
        except Exception as e:
            raise WrongDateFormatError(repr(e))
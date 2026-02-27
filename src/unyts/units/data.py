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
    """A class to represent a quantity of data with a specific unit, inheriting from the base Unit class.  The Data class is associated with the 'Data' kind in the unit dictionary and has specific units defined for data measurement."""
    class_units = _dictionary['Data']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Data object."""
        name = 'data' if name is None else name
        super().__init__(value, units, name)
        self.kind = Data
        self.__unit = self.check_unit(units)

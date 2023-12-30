#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Length', 'Area', 'Volume', 'Permeability']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Length(Unit):
    class_units = _dictionary['Length']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'length' if name is None else name
        self.kind = Length
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Area(Unit):
    class_units = _dictionary['Area']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'area' if name is None else name
        self.kind = Area
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Volume(Unit):
    class_units = _dictionary['Volume']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'volume' if name is None else name
        self.kind = Volume
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Permeability(Unit):
    class_units = _dictionary['Permeability']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'permeability' if name is None else name
        self.kind = Permeability
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.2'
__release__ = 20230107
__all__ = ['Length', 'Area', 'Volume']

from unyts.dictionaries import dictionary
from unyts.unit_class import Unit
from unyts.helpers.common_classes import unit_or_str, numeric


class Length(Unit):
    classUnits = dictionary['Length']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'length'
        self.kind = Length
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Area(Unit):
    classUnits = dictionary['Area']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'area'
        self.kind = Area
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class Volume(Unit):
    classUnits = dictionary['Volume']

    def __init__(self, value: numeric, units: unit_or_str):
        self.name = 'volume'
        self.kind = Volume
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

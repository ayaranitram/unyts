#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['Density', 'VolumeRatio', 'ProductivityIndex', 'PressureGradient']

from unyts.dictionaries import dictionary
from unyts.unit_class import Unit
from unyts.helpers.common_classes import unit_or_str, numeric


class Density(Unit):
    classUnits = dictionary['Density']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'density'
        self.kind = Density
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class VolumeRatio(Unit):
    classUnits = dictionary['VolumeRatio']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'volumeRatio'
        self.kid = VolumeRatio
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class ProductivityIndex(Unit):
    classUnits = dictionary['ProductivityIndex']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'productivityIndex'
        self.kind = ProductivityIndex
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class PressureGradient(Unit):
    classUnits = dictionary['PressureGradient']

    def __init__(self, value: numeric, units: unit_or_str) -> Unit:
        self.name = 'pressureGradient'
        self.kind = PressureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

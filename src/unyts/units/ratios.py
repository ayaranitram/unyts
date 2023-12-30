#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['Density', 'VolumeRatio', 'ProductivityIndex', 'PressureGradient']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Density(Unit):
    class_units = _dictionary['Density']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'density' if name is None else name
        self.kind = Density
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class VolumeRatio(Unit):
    class_units = _dictionary['VolumeRatio']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'volume_ratio' if name is None else name
        self.kind = VolumeRatio
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class ProductivityIndex(Unit):
    class_units = _dictionary['ProductivityIndex']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'productivity_index' if name is None else name
        self.kind = ProductivityIndex
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class PressureGradient(Unit):
    class_units = _dictionary['PressureGradient']

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'pressure_gradient' if name is None else name
        self.kind = PressureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

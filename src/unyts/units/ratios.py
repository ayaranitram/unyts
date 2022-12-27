#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['Density', 'VolumeRatio', 'ProductivityIndex', 'PressureGradient']

from ..dictionaries import dictionary
from ..unit_class import Unit


class Density(Unit):
    classUnits = dictionary['Density']

    def __init__(self, value, units):
        self.name = 'Density'
        self.kind = Density
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class VolumeRatio(Unit):
    classUnits = dictionary['VolumeRatio']

    def __init__(self, value, units):
        self.name = 'VolumeRatio'
        self.kid = VolumeRatio
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class ProductivityIndex(Unit):
    classUnits = dictionary['ProductivityIndex']

    def __init__(self, value, units):
        self.name = 'ProductivityIndex'
        self.kind = ProductivityIndex
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class PressureGradient(Unit):
    classUnits = dictionary['PressureGradient']

    def __init__(self, value, units):
        self.name = 'PressureGradient'
        self.kind = PressureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

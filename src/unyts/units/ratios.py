#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['density', 'volumeRatio', 'productivityIndex', 'pressureGradient']

from ..dictionaries import dictionary
from ..unit_class import Unit


class density(Unit):
    classUnits = dictionary['density']

    def __init__(self, value, units):
        self.name = 'density'
        self.kind = density
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class volumeRatio(Unit):
    classUnits = dictionary['volumeRatio']

    def __init__(self, value, units):
        self.name = 'volumeRatio'
        self.kid = volumeRatio
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class productivityIndex(Unit):
    classUnits = dictionary['productivityIndex']

    def __init__(self, value, units):
        self.name = 'productivityIndex'
        self.kind = productivityIndex
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)


class pressureGradient(Unit):
    classUnits = dictionary['pressureGradient']

    def __init__(self, value, units):
        self.name = 'pressureGradient'
        self.kind = pressureGradient
        self.value = self.check_value(value)
        self.unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.32'
__release__ = 20250320
__all__ = ['Density', 'VolumeRatio', 'ProductivityIndex', 'PressureGradient', 'TemperatureGradient']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Density(Unit):
    class_units = _dictionary['Density']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'density' if name is None else name
        super().__init__(value, units, name)
        self.kind = Density
        self.__unit = self.check_unit(units)


class VolumeRatio(Unit):
    class_units = _dictionary['VolumeRatio']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'volume_ratio' if name is None else name
        super().__init__(value, units, name)
        self.kind = VolumeRatio
        self.__unit = self.check_unit(units)


class ProductivityIndex(Unit):
    class_units = _dictionary['ProductivityIndex']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'productivity_index' if name is None else name
        super().__init__(value, units, name)
        self.kind = ProductivityIndex
        self.__unit = self.check_unit(units)


class PressureGradient(Unit):
    class_units = _dictionary['PressureGradient']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'pressure_gradient' if name is None else name
        super().__init__(value, units, name)
        self.kind = PressureGradient
        self.__unit = self.check_unit(units)

class TemperatureGradient(Unit):
    class_units = _dictionary['TemperatureGradient']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'temperature_gradient' if name is None else name
        super().__init__(value, units, name)
        self.kind = TemperatureGradient
        self.__unit = self.check_unit(units)

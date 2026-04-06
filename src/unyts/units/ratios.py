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


def _add_to_class_units(cls, units_str):
    """Add a validated unit string to cls.class_units and the dictionary."""
    dict_key = cls.__name__
    if isinstance(cls.class_units, tuple):
        cls.class_units = cls.class_units + (units_str,)
    else:
        cls.class_units = list(cls.class_units) + [units_str]
    _dictionary[dict_key] = cls.class_units


class Density(Unit):
    """A class to represent density units."""
    class_units = _dictionary['Density']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Density object with a value and units."""
        name = 'density' if name is None else name
        super().__init__(value, units, name)
        self.kind = Density
        self.__unit = self.check_unit(units)

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 2:
            return False
        mass, vol = parts
        if mass in _dictionary.get('Mass', ()) and vol in _dictionary.get('Volume', ()):
            _add_to_class_units(cls, units)
            return True
        return False


class VolumeRatio(Unit):
    """A class to represent volume ratio units."""
    class_units = _dictionary['VolumeRatio']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a VolumeRatio object with a value and units."""
        name = 'volume_ratio' if name is None else name
        super().__init__(value, units, name)
        self.kind = VolumeRatio
        self.__unit = self.check_unit(units)

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 2:
            return False
        num, den = parts
        volumes = _dictionary.get('Volume', ())
        if num in volumes and den in volumes:
            _add_to_class_units(cls, units)
            return True
        return False


class ProductivityIndex(Unit):
    """A class to represent productivity index units."""
    class_units = _dictionary['ProductivityIndex']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a ProductivityIndex object with a value and units."""
        name = 'productivity_index' if name is None else name
        super().__init__(value, units, name)
        self.kind = ProductivityIndex
        self.__unit = self.check_unit(units)

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 3:
            return False
        vol, time, pressure = parts
        volumes = _dictionary.get('Volume', ())
        times = _dictionary.get('Time', ())
        pressures = _dictionary.get('Pressure', ())
        if vol in volumes and time in times and pressure in pressures:
            _add_to_class_units(cls, units)
            return True
        # pressure and time components can be swapped in some cases
        if vol in volumes and time in pressures and pressure in times:
            _add_to_class_units(cls, units)
            return True
        return False


class PressureGradient(Unit):
    """A class to represent pressure gradient units."""
    class_units = _dictionary['PressureGradient']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a PressureGradient object with a value and units."""
        name = 'pressure_gradient' if name is None else name
        super().__init__(value, units, name)
        self.kind = PressureGradient
        self.__unit = self.check_unit(units)

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 2:
            return False
        pressure, length = parts
        if pressure in _dictionary.get('Pressure', ()) and length in _dictionary.get('Length', ()):
            _add_to_class_units(cls, units)
            return True
        return False


class TemperatureGradient(Unit):
    """A class to represent temperature gradient units."""
    class_units = _dictionary['TemperatureGradient']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a TemperatureGradient object with a value and units."""
        name = 'temperature_gradient' if name is None else name
        super().__init__(value, units, name)
        self.kind = TemperatureGradient
        self.__unit = self.check_unit(units)

    @classmethod
    def _dynamic_validate(cls, units: str) -> bool:
        parts = units.split('/')
        if len(parts) != 2:
            return False
        temp, length = parts
        if temp in _dictionary.get('Temperature', ()) and length in _dictionary.get('Length', ()):
            _add_to_class_units(cls, units)
            return True
        return False

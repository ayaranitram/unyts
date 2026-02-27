#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250320
__all__ = ['Force', 'Pressure', 'Weight', 'Compressibility', 'Viscosity']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Force(Unit):
    """A class to represent a force quantity with a value, unit, name, and kind.  The class_units attribute is set to the list of valid units for this kind of quantity from the dictionary."""
    class_units = _dictionary['Force']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Force object with a value and units."""
        name = 'force' if name is None else name
        super().__init__(value, units, name)
        self.kind = Force
        self.__unit = self.check_unit(units)


class Pressure(Unit):
    """A class to represent pressure quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Pressure']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Pressure object with a value and units."""
        name = 'pressure' if name is None else name
        super().__init__(value, units, name)
        self.kind = Pressure
        self.__unit = self.check_unit(units)


class Weight(Unit):
    """A class to represent weight quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Weight']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Weight object with a value and units."""
        name = 'weight' if name is None else name
        super().__init__(value, units, name)
        self.kind = Weight
        self.__unit = self.check_unit(units)


class Compressibility(Unit):
    """A class to represent compressibility quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Compressibility']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Compressibility object with a value and units."""
        name = 'compressibility' if name is None else name
        super().__init__(value, units, name)
        self.kind = Compressibility
        self.__unit = self.check_unit(units)


class Viscosity(Unit):
    """A class to represent viscosity quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Viscosity']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Viscosity object with a value and units."""
        name = 'viscosity' if name is None else name
        super().__init__(value, units, name)
        self.kind = Viscosity
        self.__unit = self.check_unit(units)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250320
__all__ = ['Length', 'Area', 'Volume', 'Permeability']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class Length(Unit):
    """A class to represent a length quantity with associated units."""
    class_units = _dictionary['Length']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Length object with a value and units."""
        name = 'length' if name is None else name
        super().__init__(value, units, name)
        self.kind = Length
        self.__unit = self.check_unit(units)


class Area(Unit):
    """A class to represent area quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Area']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize an Area object with a value and units."""
        name = 'area' if name is None else name
        super().__init__(value, units, name)
        self.kind = Area
        self.__unit = self.check_unit(units)


class Volume(Unit):
    """A class to represent volume quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Volume']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Volume object with a value and units."""
        name = 'volume' if name is None else name
        super().__init__(value, units, name)
        self.kind = Volume
        self.__unit = self.check_unit(units)


class Permeability(Unit):
    """A class to represent permeability quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Permeability']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Permeability object with a value and units."""
        name = 'permeability' if name is None else name
        super().__init__(value, units, name)
        self.kind = Permeability
        self.__unit = self.check_unit(units)

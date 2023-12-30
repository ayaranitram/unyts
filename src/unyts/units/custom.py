#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['CustomUnits', 'UserUnits', 'OtherUnits', 'set_unit', 'set_conversion']

from ..unit_class import Unit
from ..dictionaries import dictionary
from ..helpers.common_classes import unit_or_str, numeric


def CustomUnits(value: numeric, units: unit_or_str, name=None) -> Unit:
    return UserUnits(value, units, name)


def OtherUnits(value: numeric, units: unit_or_str, name=None) -> Unit:
    return UserUnits(value, units, name)


class UserUnits(Unit):
    class_units = dictionary['UserUnits']
    __slots__ = ('unit', 'value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        self.name = 'user_units' if name is None else name
        self.kind = UserUnits
        units = units.strip()
        if isinstance(units, Unit):
            units = units.unit
        if units not in dictionary['UserUnits']:
            if type(dictionary['UserUnits']) is tuple:
                dictionary['UserUnits'] = list(dictionary['UserUnits'])
            dictionary['UserUnits'].append(units)
        self.value = self.check_value(value)
        self.unit = units  # self.check_unit(units)


def set_unit(unit_name: str) -> bool:
    from ..database import units_network
    from ..network import UNode
    units_network.add_node(UNode(unit_name))


def set_conversion(from_units: str, to_units: str, conversion, reverse_conversion=None) -> bool:
    from ..database import units_network
    from ..network import UNode, Conversion
    if reverse_conversion is None:
        def reverse_conversion(x): return x / conversion(1)
    if type(from_units) is str:
        pass
    elif hasattr(from_units, 'units') and type(from_units.units) is str:
        from_units = from_units.units
    else:
        raise TypeError("`from_units` must be str or Unit.")
    if type(to_units) is str:
        pass
    elif hasattr(to_units, 'units') and type(to_units.units) is str:
        to_units = to_units.units
    else:
        raise TypeError("`to_units` must be str or Unit.")
    if not hasattr(conversion, '__call__') and hasattr(conversion, '__getitem__'):
        raise TypeError("`conversion` must be callable.")
    if not hasattr(reverse_conversion, '__call__') and hasattr(reverse_conversion, '__getitem__'):
        raise TypeError("`reverse_conversion` must be callable.")

    units_network.add_node(UNode(from_units))
    units_network.add_node(UNode(to_units))
    units_network.add_edge(Conversion(units_network.get_node(from_units),
                                      units_network.get_node(to_units),
                                      conversion))
    units_network.add_edge(Conversion(units_network.get_node(to_units),
                                      units_network.get_node(from_units),
                                      reverse_conversion))

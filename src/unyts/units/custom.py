#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.32'
__release__ = 20260225
__all__ = ['CustomUnits', 'UserUnits', 'OtherUnits', 'set_unit', 'set_conversion']

from ..unit_class import Unit
from ..dictionaries import dictionary
from ..helpers.common_classes import unit_or_str, numeric


def CustomUnits(value: numeric, units: unit_or_str, name=None) -> Unit:
    """Factory function for creating custom units that are not part of the standard unit definitions."""
    return UserUnits(value, units, name)


def OtherUnits(value: numeric, units: unit_or_str, name=None) -> Unit:
    """Generic factory for creating units that are not part of the standard unit definitions.  
    This is an alias for `CustomUnits` and is provided for semantic clarity when creating units that are not necessarily user-defined but are still outside the standard definitions."""
    return UserUnits(value, units, name)


class UserUnits(Unit):
    """A class to represent user-defined units that are not part of the standard unit definitions.  
    This class is used for units that are added by the user at runtime using the `set_unit` function, and for units that are defined in the `custom.py` module.  
    The unit names are stored in the `UserUnits` entry of the `dictionary`, and any unit name that is not in the standard unit definitions can be used as a UserUnit.  
    The conversion functions for UserUnits must be defined by the user using the `set_conversion` function."""
    class_units = dictionary['UserUnits']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a UserUnits object."""
        name = 'user_units' if name is None else name
        super().__init__(value, None, name)
        self.kind = UserUnits
        units = units.strip()
        if isinstance(units, Unit):
            units = units.unit
        if units not in dictionary['UserUnits']:
            if type(dictionary['UserUnits']) is tuple:
                dictionary['UserUnits'] = list(dictionary['UserUnits'])
            dictionary['UserUnits'].append(units)
        self.unit = units  # self.check_unit(units)


def set_unit(unit_name: str) -> bool:
    """Add a new unit name to the UserUnits class and the database."""
    from ..database import units_network
    from ..network import UNode
    unit_name = unit_name.strip()
    if type(dictionary['UserUnits']) is tuple:
        dictionary['UserUnits'] = list(dictionary['UserUnits'])
    if unit_name not in dictionary['UserUnits']:
        dictionary['UserUnits'].append(unit_name)
    units_network.add_node(UNode(unit_name))
    # Invalidate stale cached searches that involve this user unit.
    units_network.memory = {k: v for k, v in units_network.memory.items() if unit_name not in k}
    units_network.previous = [k for k in units_network.previous if unit_name not in k]
    return True


def set_conversion(from_units: str, to_units: str, conversion, reverse_conversion=None) -> bool:
    """Set a conversion function between two units, this adds a directed edge to the units network.  
    If `reverse_conversion` is not provided, the reverse conversion will be automatically generated as `lambda x: x / conversion(1)`, 
    which is correct for linear conversions but may not be correct for more complex conversions (e.g. temperature)."""
    from ..database import units_network
    from ..network import UNode, Conversion
    if reverse_conversion is None:
        def reverse_conversion(x):
            """Apply a default reverse conversion for linear relationships."""
            return x / conversion(1)
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

    if type(dictionary['UserUnits']) is tuple:
        dictionary['UserUnits'] = list(dictionary['UserUnits'])
    if from_units not in dictionary['UserUnits']:
        dictionary['UserUnits'].append(from_units)
    if to_units not in dictionary['UserUnits']:
        dictionary['UserUnits'].append(to_units)

    units_network.add_node(UNode(from_units))
    units_network.add_node(UNode(to_units))

    def _upsert_edge(src_name, dst_name, conv):
        """Insert edge if missing, otherwise replace conversion callable."""
        src = units_network.get_node(src_name)
        dst = units_network.get_node(dst_name)
        children = units_network.edges[src][0]
        converters = units_network.edges[src][1]
        if dst in children:
            converters[children.index(dst)] = conv
        else:
            units_network.add_edge(Conversion(src, dst, conv))

    _upsert_edge(from_units, to_units, conversion)
    _upsert_edge(to_units, from_units, reverse_conversion)

    # Reset cached string representation of edges so search algorithms that rely
    # on it (e.g. lean_BFS via _get_descendants) see the new conversion edge.
    try:
        units_network._edges_str = None
    except Exception:
        pass

    # Clear stale cache entries from previous failed searches or older custom mappings.
    impacted = {from_units, to_units}
    units_network.memory = {
        k: v for k, v in units_network.memory.items()
        if (k[0] not in impacted and k[1] not in impacted)
    }
    units_network.previous = [
        k for k in units_network.previous
        if (k[0] not in impacted and k[1] not in impacted)
    ]
    return True

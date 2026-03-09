#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.30'
__release__ = 20230724
__all__ = ['units']

from ..dictionaries import dictionary as _dictionary, uncertain_names
from .custom import UserUnits
from .data import *
from .date import *
from .energy import *
from .force import *
from .geometry import *
from .mass import *
from .rates import *
from .ratios import *
from .temperature import *
from .time import *
from .unitless import Dimensionless, Percentage
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str as unit_or_str, numeric as numeric, numeric_ as _numeric


def units(value: numeric, unit: unit_or_str=None, name=None) -> Unit:
    """
    return an instance of units with the provided value and units.

    Parameters
    ----------
    value : int, float, numeric array, Series or DataFrame
        the value to assign the units.
    unit : str, optional
        the units to assign the value. The default is None.
    name : str, optional
        a string available to user to store metadata.

    Raises
    ------
    TypeError
        if value or units are not the appropriate kind.

    Returns
    -------
    units
        instance of units.

    """
    if unit is None and isinstance(value, Unit):
        value, unit = value.value, value.units
    if unit is None:
        unit = 'Dimensionless'
    if type(unit) is not str:
        raise TypeError("'units' must be a string or Unit instance.")
    if not isinstance(value, _numeric) and not ((type(unit) is str and unit == 'date') or type(unit) is Date):
        raise TypeError("'value' parameter must be numeric.")

    unit = unit.strip()

    # perform canonical alias lookup early so that later code only deals
    # with names that actually appear in the dictionary structure.  We do not
    # attempt to disambiguate here; if the alias is truly ambiguous the
    # recursive search below will still find a matching canonical name when it
    # exists.
    from ..dictionaries import canonical_name
    unit = canonical_name(unit)

    if unit in uncertain_names:
        return Unit(value, unit, name)
    if (type(unit) is str and unit == 'date') or type(unit) is Date:
        return Date(value, 'date', name)

    # helper that knows how to search arbitrary dictionary entries
    def _in_dict(u, val):
        if isinstance(val, (list, tuple, set)):
            return u in val
        elif isinstance(val, dict):
            # check both keys (canonical names) and alias lists
            if u in val:
                return True
            for aliases in val.values():
                if isinstance(aliases, (list, tuple, set)):
                    if u in aliases:
                        return True
                elif isinstance(aliases, str):
                    if u == aliases:
                        return True
        return False

    for kind in _dictionary:
        if _in_dict(unit, _dictionary[kind]):
            if "'" in unit:
                u = eval(kind + '''(0, "''' + unit + '''")''', name)
            else:
                u = eval(kind + """(0, '""" + unit + """')""", name)
            if type(u) is Percentage:
                u.value = value / 100
            else:
                u.value = value
            return u

    return UserUnits(value, unit, name)

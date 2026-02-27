# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:46:04 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20230118
__all__ = ['is_unit']

from ..dictionaries import dictionary as _dictionary


def is_unit(unit: str) -> bool:
    """Return True if the given string is a valid unit in the unyts system, False otherwise.  
    This function checks against the unit definitions in the unyts dictionary, including handling compound units with '/' and '*' operators."""
    if type(unit) is str:
        unit = unit.strip()
    else:
        raise TypeError("unit must be a string.")

    for each in list(_dictionary.keys()):
        if '_' not in each:
            is_u = unit in list(_dictionary[each])
            if is_u:
                return True

    if '/' in unit or '*' in unit:
        unit_split = []
        for each in unit.split('/'):
            unit_split += each.split('*')
        ret = [False] * len(unit_split)
        for each in list(_dictionary.keys()):
            if '_' not in each:
                for sub_u in range(len(unit_split)):
                    if unit_split[sub_u] in list(_dictionary[each]):
                        ret[sub_u] = True
        for each in ret:
            if not each:
                return False
        return True
    return False

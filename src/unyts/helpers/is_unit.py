# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:46:04 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['is_unit']

from unyts.dictionaries import dictionary


def is_unit(unit: str) -> bool:
    if type(unit) is str:
        unit = unit.strip()
    else:
        raise TypeError("unit must be a string.")

    for each in list(dictionary.keys()):
        if '_' not in each:
            is_u = unit in list(dictionary[each])
            if is_u:
                return True

    if '/' in unit or '*' in unit:
        unit_split = []
        for each in unit.split('/'):
            unit_split += each.split('*')
        ret = [False] * len(unit_split)
        for each in list(dictionary.keys()):
            if '_' not in each:
                for sub_u in range(len(unit_split)):
                    if unit_split[sub_u] in list(dictionary[each]):
                        ret[sub_u] = True
        for each in ret:
            if not each:
                return False
        return True
    return False

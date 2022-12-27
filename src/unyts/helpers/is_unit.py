# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:46:04 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['is_unit']

from ..dictionaries import dictionary


def is_unit(unit):
    if type(unit) is str:
        unit = unit.strip()

    for each in list(dictionary.keys()):
        if '_' not in each:
            isU = unit in list(dictionary[each])
            if isU :
                return True

    if '/' in unit or '*' in unit:
        unit_split = []
        for each in unit.split('/'):
            unit_split += each.split('*')
        ret = [False] * len(unit_split)

        for each in list(dictionary.keys()):
            if '_' not in each :
                for subU in range(len(unit_split)):
                    if unit_split[subU] in list(dictionary[each]):
                        ret[subU] = True

        for each in ret:
            if not each:
                return False

    return True

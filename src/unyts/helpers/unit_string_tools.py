#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['_split_ratio', '_split_product', '_split_unit', '_reduce_parentheses']


from unyts.helpers.multi_split import multi_split


def _split_ratio(unit: str) -> tuple[str]:
    return tuple(map(str.strip, unit.split('/')))


def _split_product(unit: str) -> tuple[str]:
    return tuple(map(str.strip, unit.split('*')))


def _split_unit(unit: str) -> tuple[str]:
    return multi_split(unit,
                       sep=('*', '/',),
                       remove=None)


def _reduce_parentheses(unit: str) -> str:
    if '(' not in unit and ')' not in unit:
        return unit
    elif unit.count('(') > unit.count(')'):
        raise ValueError("closing parenthesis without opening parenthesis")
    elif unit.count('(') < unit.count(')'):
        raise ValueError("opening parenthesis without closing parenthesis")
    for o in ['^', '**', '+', '-']:
        if o in unit:
            print("not implemented to remove parenthesis when ' + o + ' is in the unit string")
            return unit

    unit_split = multi_split(unit,
                             sep=('+', '-', '*', '/', '**', '(', ')'),
                             remove=' ')
    result, inv, inp, ii, pa = [], False, False, 0, 0
    while ii < len(unit_split):
        if unit_split[ii] in '*/' and inp and inv:
            result.append('*' if unit_split[ii] == '/' else '/')
        elif unit_split[ii] not in '()':
            result.append(unit_split[ii])
        if unit_split[ii] == '/' and unit_split[ii + 1] == '(':
            inv = not inv
        elif unit_split[ii] == '(':
            inp, pa = True, pa + 1
        elif unit_split[ii] == ')':
            inp, pa = False, pa - 1
        ii += 1
    return ''.join(result)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.2'
__release__ = 20230118
__all__ = ['split_ratio', 'split_product', 'split_unit', 'reduce_parentheses', 'reduce_units']

from .multi_split import multi_split


def split_ratio(unit: str) -> list:  # list[str]  not sub-typing in order to be compatible with Python 3.7 - 3.9
    return list(map(str.strip, unit.split('/')))


def split_product(unit: str) -> list:  # list[str]  not sub-typing in order to be compatible with Python 3.7 - 3.9
    return list(map(str.strip, unit.split('*')))


def split_unit(unit: str) -> list:
    return multi_split(unit,
                       sep=('*', '/',),
                       remove=None)


def reduce_parentheses(unit: str) -> str:
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
                             sep=('+', '-', '*', '/', '^', '**', '(', ')'),
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


def reduce_units(unit: str, raise_error=False) -> str:
    def change(unit_):
        return ('/' + unit_[1:]) if unit_[0] == '*' else ('*' + unit_[1:])

    if raise_error:
        if unit is None:
            raise ValueError("`unit_string` must be an str.")
        if '+' in unit or '-' in unit:
            raise NotImplementedError("`unit_reduce` for units with addition is not implemented.")
    else:
        if unit is None:
            return None
        if '+' in unit or '-' in unit:
            return unit

    if '/' in unit:
        unit_split = multi_split('*' + unit,
                                 sep=('+', '-', '*', '/', '^', '**', '(', ')'),
                                 remove=' ')
        unit_split = [(unit_split[i] + unit_split[i + 1]) for i in range(0, len(unit_split) - 1, 2)]
        i, simplified, ignore = 0, [], []
        while i < len(unit_split):
            if i in ignore:
                pass
            elif change(unit_split[i]) in unit_split[i + 1:]:
                ignore.append(unit_split[i + 1:].index(change(unit_split[i])) + i + 1)
            else:
                simplified.append(unit_split[i])
            i += 1

        if len(simplified) == 0:
            return unit
        result = ''.join(simplified).strip('*')
        if result.startswith('/'):
            result = '1' + result
        return result
    else:
        return unit

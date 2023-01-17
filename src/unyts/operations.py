#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:38:58 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.2'
__release__ = 20230116
__all__ = ['unit_product', 'unit_division', 'unit_base_power', 'unit_power', 'unit_addition', 'unit_inverse']

from unyts.dictionaries import dictionary, unitless_names
from unyts.converter import convertible
from unyts.helpers.is_number import is_number
from unyts.helpers.unit_string_tools import reduce_units
from unyts.helpers.multi_split import multi_split


def unit_split(unit_string: str) -> str:
    us = multi_split(unit_string)
    return us


def unit_base_power(unit_string: str) -> tuple:  # tuple[str, int]
    u_bas, u_pow = '', ''
    oth = ''
    inv = False
    if '/' in unit_string and len(unit_string.split('/')) == 2 and is_number(unit_string.split('/')[0]):
        inv_pow, u_bas = unit_string.split('/')
        inv = True
    else:
        for c in unit_string:
            if c.isdigit():
                u_pow += oth + c
                oth = ''
            elif c in ['-', '+', '.']:
                oth += c
            else:
                if inv and len(u_pow) > 0:
                    if u_pow[0] == '-':
                        u_pow = u_pow[1:]
                    else:
                        u_pow = '-' + u_pow
                if c in ['/']:
                    inv = not inv
                u_bas += oth + c
                oth = ''
        if inv and len(u_pow) > 0:
            if u_pow[0] == '-':
                u_pow = u_pow[1:]
            else:
                u_pow = '-' + u_pow
        inv = False
    u_pow = 1 if u_pow == '' else float(u_pow) if '.' in u_pow else int(u_pow)
    if inv:
        u_pow = u_pow * -1 * (float(inv_pow) if '.' in inv_pow else int(inv_pow))
    return u_bas, u_pow


def unit_base(unit_string: str) -> str:
    return unit_base_power(unit_string)[0]


def unit_product(unit_string1: str, unit_string2: str) -> str:
    if unit_string1 is None:
        unit_string1 = 'dimensionless'
    if unit_string2 is None:
        unit_string2 = 'dimensionless'

    if type(unit_string1) is str and len(unit_string1.strip(' ()')) == 0:
        unit_string1 = 'dimensionless'
    if type(unit_string2) is str and len(unit_string2.strip(' ()')) == 0:
        unit_string2 = 'dimensionless'

    if type(unit_string1) is str and len(unit_string1.split('/')) == 2 and unit_string1.split('/')[0] == \
            unit_string1.split('/')[1]:
        unit_string1 = 'dimensionless'
    if type(unit_string2) is str and len(unit_string2.split('/')) == 2 and unit_string2.split('/')[0] == \
            unit_string2.split('/')[1]:
        unit_string2 = 'dimensionless'

    if unit_string2.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        return unit_string1
    if unit_string1.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        if unit_string2.lower().strip(' ()') not in unitless_names:  # dictionary['Dimensionless']:
            return unit_string2
        else:
            return unit_string1

    if unit_string1 != unit_string2 and convertible(unit_string1, unit_string2):
        return unit_product(unit_string1, unit_string1)

    u1bas, u1pow = unit_base_power(unit_string1)
    u2bas, u2pow = unit_base_power(unit_string2)

    if u1pow == -1 and u2pow != -1:
        return unit_division(unit_string2, u1bas)
    elif u1pow != -1 and u2pow == -1:
        return unit_division(unit_string1, u2bas)

    if convertible(u1bas, u2bas):
        u_pow = u1pow + u2pow
        if u_pow == -1:
            result = u1bas + '-1'
        elif u_pow == 1:
            result = u1bas
        elif u_pow == 0:
            result = u1bas + '/' + u1bas
        else:
            for c in ['+', '-', '^']:  # '*','/'
                if c in u1bas:
                    u1bas = '(' + u1bas + ')'
                    break
            result = u1bas + str(u_pow)
    else:
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string1:
                unit_string1 = '(' + unit_string1 + ')'
                break
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string2:
                unit_string2 = '(' + unit_string2 + ')'
                break
        result = unit_string1 + '*' + unit_string2
    return reduce_units(result, raise_error=False)


def unit_division(unit_string1: str, unit_string2: str) -> str:
    if unit_string1 is None:
        unit_string1 = 'dimensionless'
    if unit_string2 is None:
        unit_string2 = 'dimensionless'

    if type(unit_string1) is str and len(unit_string1.strip(' ()')) == 0:
        unit_string1 = 'dimensionless'
    if type(unit_string2) is str and len(unit_string2.strip(' ()')) == 0:
        unit_string2 = 'dimensionless'

    if type(unit_string1) is str and len(unit_string1.split('/')) == 2 and unit_string1.split('/')[0] == \
            unit_string1.split('/')[1]:
        unit_string1 = 'dimensionless'
    if type(unit_string2) is str and len(unit_string2.split('/')) == 2 and unit_string2.split('/')[0] == \
            unit_string2.split('/')[1]:
        unit_string2 = 'dimensionless'

    if unit_string2.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        return unit_string1
    if unit_string1.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        if unit_string2.lower().strip(' ()') not in unitless_names:  # dictionary['Dimensionless']:
            u_bas, u_pow = unit_base_power('1/' + unit_string2)
            return u_bas + str(u_pow)
        else:
            return unit_string1

    if unit_string1 != unit_string2 and convertible(unit_string1, unit_string2):
        return unit_division(unit_string1, unit_string1)

    u1bas, u1pow = unit_base_power(unit_string1)
    u2bas, u2pow = unit_base_power(unit_string2)

    if u1pow == -1 and u2pow != -1:
        return unit_product(u1bas, unit_string2)
    elif u1pow != -1 and u2pow == -1:
        return unit_product(unit_string1, u2bas)

    if convertible(u1bas, u2bas):
        u_pow = u1pow - u2pow
        if u_pow == -1:
            result = u1bas + '-1'
        elif u_pow == 1:
            result = u1bas
        elif u_pow == 0:
            result = u1bas + '/' + u1bas
        else:
            for c in ['+', '-', '^']:  # '*','/'
                if c in u1bas:
                    u1bas = '(' + u1bas + ')'
                    break
            result = u1bas + str(u_pow)

    elif ('+' not in unit_string1 and '-' not in unit_string1 and '^' not in unit_string1) and (
            '+' not in unit_string2 and '-' not in unit_string2 and '^' not in unit_string2) and (
            '*' in unit_string1 and unit_base(unit_string2) in map(unit_base, unit_string1.split('*'))):
        result = ''
        for u in unit_string1.split('*'):
            if unit_string2 == u:
                return '*'.join([u for u in unit_string1.split('*') if u != unit_string2])
            elif unit_base(unit_string2) == unit_base(u):
                result = (result + '*' + unit_division(u, unit_string2).strip('*')).strip('*')
            else:
                result = (result + '*' + u).strip('*')
    else:
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string1:
                unit_string1 = '(' + unit_string1 + ')'
                break
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string2:
                unit_string2 = '(' + unit_string2 + ')'
                break
        result = unit_string1 + '/' + unit_string2
    return reduce_units(result, raise_error=False)


def unit_power(unit_string: str, power: int or str) -> str:
    if unit_string is None:
        unit_string = 'dimensionless'
    if power is None:
        power = 1

    if type(unit_string) is str and len(unit_string.strip(' ()')) == 0:
        unit_string = 'dimensionless'
    if type(power) is str and len(power.strip(' ()')) == 0:
        power = 1

    u1bas, u1pow = unit_base_power(unit_string)

    if type(power) in (int, float):
        u_pow = u1pow * power
        if u_pow == 0:
            return 'dimensionless'
        elif u_pow == 1:
            return u1bas
        else:
            return u1bas + str(u_pow)
    elif type(power) is str:
        u2bas, u2pow = unit_base_power(power)
        u_pow = u1pow * u2pow
        if u_pow == 0:
            return 'dimensionless'
        elif u_pow == 1:
            return u1bas + '^' + u2bas
        else:
            return u1bas + '^' + str(u_pow) + u2bas
    else:
        raise TypeError('Power must be units string or numeric.')


def unit_addition(unit_string1:str, unit_string2:str) -> str:
    if unit_string1 is None:
        unit_string1 = 'dimensionless'
    if unit_string2 is None:
        unit_string2 = 'dimensionless'

    if unit_string2.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        return unit_string1
    if unit_string1.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        if unit_string2.lower().strip(' ()') not in unitless_names:  # dictionary['Dimensionless']:
            return unit_string2
        else:
            return unit_string1

    if convertible(unit_string2, unit_string1):
        return unit_string1
    elif convertible(unit_string1, unit_string2):
        return unit_string2
    else:
        return unit_string1 + '+' + unit_string2


def unit_inverse(unit_string: str) -> str:
    if unit_string is None:
        unit_string = 'dimensionless'

    if type(unit_string) is str and len(unit_string.strip(' ()')) == 0:
        unit_string = 'dimensionless'

    if unit_string.lower().strip(' ()') in unitless_names:  # dictionary['Dimensionless']:
        return unit_string

    ubas, upow = unit_base_power(unit_string)
    if upow == -1:
        return ubas
    elif upow < -1:
        return ubas + str(abs(upow))
    elif upow > 1:
        return ubas + str(-1 * upow)

    if '/' not in unit_string:
        return ubas + '-1'  # '1/' + ubas
    elif len(unit_string.split('/')) == 2:
        return unit_string.split('/')[1] + '/' + unit_string.split('/')[0]
    elif len(unit_string.split('/')) == 3:
        return unit_string.split('/')[2] + '*' + unit_string.split('/')[1] + '/' + unit_string.split('/')[0]
    else:  # wtf?
        return '/'.join(unit_string.split('/')[::-1])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:38:58 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['unit_product', 'unit_division']

from .dictionaries import dictionary
from .converter import convertible
from .helpers.is_number import is_number
from .helpers.multi_split import multi_split


def unit_split(unit_string) -> str:
    us = multi_split(unit_string)
    return us


def unit_base_power(unit_string) -> (str, str):
    u_bas, u_pow = '', ''
    oth = ''
    inv = False
    if '/' in unit_string and len(unit_string.split('/')) == 2 and is_number(unit_string.split('/')[0]):
        inv_pow, unit_string = unit_string.split('/')
        inv = True

    for c in unit_string:
        if c.isdigit():
            u_pow += oth + c
            oth = ''
        elif c in ['-', '+', '.']:
            oth += c
        else :
            u_bas += oth + c
            oth = ''
    u_pow = 1 if u_pow == '' else float(u_pow) if '.' in u_pow else int(u_pow)
    if inv:
        u_pow = u_pow * -1 * (float(inv_pow) if '.' in inv_pow else int(inv_pow))
    return u_bas, u_pow


def unit_base(unit_string) -> str:
    return unit_base_power(unit_string)[0]


def unit_product(unit_string1, unit_string2) -> str:
    if unit_string1 is None:
        unit_string1 = 'Dimensionless'
    if unit_string2 is None:
        unit_string2 = 'Dimensionless'

    if type(unit_string1) is str and len(unit_string1.strip(' ()')) == 0:
        unit_string1 = 'Dimensionless'
    if type(unit_string2) is str and len(unit_string2.strip(' ()')) == 0:
        unit_string2 = 'Dimensionless'

    if type(unit_string1) is str and len(unit_string1.split('/')) == 2 and unit_string1.split('/')[0] == unit_string1.split('/')[1]:
        unit_string1 = 'Dimensionless'
    if type(unit_string2) is str and len(unit_string2.split('/')) == 2 and unit_string2.split('/')[0] == unit_string2.split('/')[1]:
        unit_string2 = 'Dimensionless'

    if unit_string2.lower().strip(' ()') in dictionary['dimensionless']:
        return unit_string1
    if unit_string1.lower().strip(' ()') in dictionary['dimensionless']:
        if unit_string2.lower().strip(' ()') not in dictionary['dimensionless']:
            return unit_string2
        else :
            return unit_string1

    if unit_string1 != unit_string2 and convertible(unit_string1, unit_string2):
        return unit_product(unit_string1, unit_string1)

    u1bas, u1pow = unit_base_power(unit_string1)
    u2bas, u2pow = unit_base_power(unit_string2)

    if convertible(u1bas, u2bas):
        u_pow = u1pow+u2pow
        if u_pow == -1:
            result = u1bas+'-1'
        elif u_pow == 1:
            result = u1bas
        elif u_pow == 0:
            result = u1bas + '/' + u1bas
        else :
            for c in ['+', '-', '^']:  # '*','/'
                if c in u1bas:
                    u1bas = '('+u1bas+')'
                    break
            result = u1bas + str(u_pow)
    else:
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string1:
                unit_string1 = '('+unit_string1+')'
                break
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string2:
                unit_string2 = '('+unit_string2+')'
                break
        result = unit_string1 + '*' + unit_string2
    return result


def unit_division(unit_string1, unit_string2) -> str:
    if unit_string1 is None:
        unit_string1 = 'dimensionless'
    if unit_string2 is None:
        unit_string2 = 'dimensionless'

    if type(unit_string1) is str and len(unit_string1.strip(' ()')) == 0:
        unit_string1 = 'dimensionless'
    if type(unit_string2) is str and len(unit_string2.strip(' ()')) == 0:
        unit_string2 = 'dimensionless'

    if type(unit_string1) is str and len(unit_string1.split('/')) == 2 and unit_string1.split('/')[0] == unit_string1.split('/')[1]:
        unit_string1 = 'dimensionless'
    if type(unit_string2) is str and len(unit_string2.split('/')) == 2 and unit_string2.split('/')[0] == unit_string2.split('/')[1]:
        unit_string2 = 'dimensionless'

    if unit_string2.lower().strip(' ()') in dictionary['dimensionless']:
        return unit_string1
    if unit_string1.lower().strip(' ()') in dictionary['dimensionless']:
        if unit_string2.lower().strip(' ()') not in dictionary['dimensionless']:
            u_bas, u_pow = unit_base_power('1/' + unit_string2)
            return u_bas+str(u_pow)
        else:
            return unit_string1

    if unit_string1 != unit_string2 and convertible(unit_string1, unit_string2):
        return unit_division(unit_string1, unit_string1)

    u1bas, u1pow = unit_base_power(unit_string1)
    u2bas, u2pow = unit_base_power(unit_string2)

    if convertible(u1bas, u2bas):
        Upow = u1pow - u2pow
        if Upow == -1:
            result = u1bas + '-1'
        elif Upow == 1:
            result = u1bas
        elif Upow == 0:
            result = u1bas + '/' + u1bas
        else:
            for c in ['+','-','^']:  # '*','/'
                if c in u1bas:
                    u1bas = '('+u1bas+')'
                    break
            result = u1bas + str(Upow)

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
                unit_string1 = '('+unit_string1+')'
                break
        for c in ['+', '-', '^']:  # '*','/'
            if c in unit_string2:
                unit_string2 = '('+unit_string2+')'
                break
        result = unit_string1 + '/' + unit_string2
    return result


def unit_power(unit_string, power) -> str:
    if unit_string is None:
        unit_string = 'Dimensionless'
    if power is None:
        power = 1

    if type(unit_string) is str and len(unit_string.strip(' ()')) == 0:
        unit_string = 'Dimensionless'
    if type(power) is str and len(power.strip(' ()')) == 0:
        power = 1

    u1bas, u1pow = unit_base_power(unit_string)

    if type(power) in (int, float):
        u_pow = u1pow * power
        if u_pow == 0:
            return 'Dimensionless'
        elif u_pow == 1:
            return u1bas
        else:
            return u1bas + str(u_pow)
    elif type(power) is str:
        u2bas, u2pow = unit_base_power(power)
        u_pow = u1pow * u2pow
        if u_pow == 0:
            return 'Dimensionless'
        elif u_pow == 1:
            return u1bas + '^' + u2bas
        else:
            return u1bas + '^' + str(u_pow) + u2bas
    else:
        raise TypeError('power must be units string or numeric')

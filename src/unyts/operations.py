#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:38:58 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['unitProduct','unitDivision']

from .dictionaries import dictionary
from .convert import convertible
from .helpers.is_number import is_number
from .helpers.multisplit import multisplit


def unitSplit(unit_string):
    us = multisplit(unit_string)
    return us


def unitBasePower(unit_string):
    uBas, uPow = '', ''
    oth = ''
    inv = False
    if '/' in unit_string and len(unit_string.split('/')) == 2 and is_number(unit_string.split('/')[0]):
        invPow, unit_string = unit_string.split('/')
        inv = True

    for c in unit_string :
        if c.isdigit() :
            uPow += oth + c
            oth = ''
        elif c in ['-','+','.']:
            oth += c
        else :
            uBas += oth + c
            oth = ''
    uPow = 1 if uPow == '' else float(uPow) if '.' in uPow else int(uPow)
    if inv :
        uPow = uPow * -1 * (float(invPow) if '.' in invPow else int(invPow))
    return uBas, uPow


def unitBase(unit_string):
    return unitBasePower(unit_string)[0]


def unitProduct(unit_string1,unit_string2):
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
            return unit_string2
        else :
            return unit_string1

    if unit_string1 != unit_string2 and convertible(unit_string1, unit_string2):
        return unitProduct(unit_string1, unit_string1)

    U1bas, U1pow = unitBasePower(unit_string1)
    U2bas, U2pow = unitBasePower(unit_string2)

    if convertible(U1bas, U2bas):
        Upow = U1pow+U2pow
        if Upow == -1:
            result = U1bas+'-1'
        elif Upow == 1:
            result = U1bas
        elif Upow == 0:
            result = U1bas + '/' + U1bas
        else :
            for c in ['+','-','^']:  # '*','/'
                if c in U1bas:
                    U1bas = '('+U1bas+')'
                    break
            result = U1bas + str(Upow)
    else:
        for c in ['+','-','^']:  # '*','/'
            if c in unit_string1:
                unit_string1 = '('+unit_string1+')'
                break
        for c in ['+','-','^']:  # '*','/'
            if c in unit_string2:
                unit_string2 = '('+unit_string2+')'
                break
        result = unit_string1 + '*' + unit_string2
    return result


def unitDivision(unit_string1, unit_string2):
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
            uBas, uPow = unitBasePower('1/' + unit_string2)
            return uBas+str(uPow)
        else:
            return unit_string1

    if unit_string1 != unit_string2 and convertible(unit_string1, unit_string2):
        return unitDivision(unit_string1, unit_string1)

    U1bas, U1pow = unitBasePower(unit_string1)
    U2bas, U2pow = unitBasePower(unit_string2)

    if convertible(U1bas, U2bas):
        Upow = U1pow - U2pow
        if Upow == -1:
            result = U1bas + '-1'
        elif Upow == 1:
            result = U1bas
        elif Upow == 0:
            result = U1bas + '/' + U1bas
        else:
            for c in ['+','-','^']:  # '*','/'
                if c in U1bas:
                    U1bas = '('+U1bas+')'
                    break
            result = U1bas + str(Upow)

    elif ('+' not in unit_string1 and '-' not in unit_string1 and '^' not in unit_string1) and (
            '+' not in unit_string2 and '-' not in unit_string2 and '^' not in unit_string2) and (
                '*' in unit_string1 and unitBase(unit_string2) in map(unitBase, unit_string1.split('*'))):
            result = ''
            for u in unit_string1.split('*'):
                if unit_string2 == u:
                    return '*'.join([u for u in unit_string1.split('*') if u != unit_string2])
                elif unitBase(unit_string2) == unitBase(u):
                    result = (result + '*' + unitDivision(u, unit_string2).strip('*')).strip('*')
                else:
                    result = (result + '*' + u).strip('*')
    else:
        for c in ['+','-','^']:  # '*','/'
            if c in unit_string1:
                unit_string1 = '('+unit_string1+')'
                break
        for c in ['+','-','^']:  # '*','/'
            if c in unit_string2:
                unit_string2 = '('+unit_string2+')'
                break
        result = unit_string1 + '/' + unit_string2
    return result
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:38:58 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__all__ = ['unitProduct','unitDivision']
__version__ = '0.1.3'
__release__ = 20220819

from ._dictionaries import dictionary
from ._convert import convertible
from ._helpers import isnumber


def unitBasePower(unit):
    """

    Parameters
    ----------
    unit : str
        a string representing the unit


    Returns
    -------
        tuple of base and power

    """
    uBas , uPow = '' , ''
    oth = ''
    inv = False
    if '/' in unit and len(unit.split('/')) > 1 and isnumber(unit.split('/')[0]):
        unit = unit.split('/')[1]
        invPow = unit.split('/')[0]
        inv = True

    # if unit.startswith('1/'):
    #     unit = unit[2:]
    #     inv = True
    for c in unit :
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
        uPow = uPow * -1 * invPow
    return uBas,uPow


def unitBase(unit):
    """
    

    Parameters
    ----------
    unit : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    return unitBasePower(unit)[0]


def unitProduct(unit1,unit2):
    """

    Parameters
    ----------
    unit1 :

    unit2 :


    Returns
    -------

    """

    if unit1 is None:
        unit1 = 'dimensionless'
    if unit2 is None:
        unit2 = 'dimensionless'

    if type(unit1) is str and len(unit1.strip(' ()')) == 0:
        unit1 = 'dimensionless'
    if type(unit2) is str and len(unit2.strip(' ()')) == 0:
        unit2 = 'dimensionless'

    if type(unit1) is str and len(unit1.split('/')) == 2 and unit1.split('/')[0] == unit1.split('/')[1]:
        unit1 = 'dimensionless'
    if type(unit2) is str and len(unit2.split('/')) == 2 and unit2.split('/')[0] == unit2.split('/')[1]:
        unit2 = 'dimensionless'

    if unit2.lower().strip(' ()') in dictionary['dimensionless']:
        return unit1
    if unit1.lower().strip(' ()') in dictionary['dimensionless']:
        if unit2.lower().strip(' ()') not in dictionary['dimensionless']:
            return unit2
        else :
            return unit1

    if unit1 != unit2 and convertible(unit1, unit2):
        return unitProduct(unit1, unit1)

    U1bas, U1pow = unitBasePower(unit1)
    U2bas, U2pow = unitBasePower(unit2)

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
            if c in unit1:
                unit1 = '('+unit1+')'
                break
        for c in ['+','-','^']:  # '*','/'
            if c in unit2:
                unit2 = '('+unit2+')'
                break
        result = unit1 + '*' + unit2

    return result


def unitDivision(unit1, unit2):
    """

    Parameters
    ----------
    unit1 :

    unit2 :


    Returns
    -------

    """

    if unit1 is None:
        unit1 = 'dimensionless'
    if unit2 is None:
        unit2 = 'dimensionless'

    if type(unit1) is str and len(unit1.strip(' ()')) == 0:
        unit1 = 'dimensionless'
    if type(unit2) is str and len(unit2.strip(' ()')) == 0:
        unit2 = 'dimensionless'

    if type(unit1) is str and len(unit1.split('/')) == 2 and unit1.split('/')[0] == unit1.split('/')[1]:
        unit1 = 'dimensionless'
    if type(unit2) is str and len(unit2.split('/')) == 2 and unit2.split('/')[0] == unit2.split('/')[1]:
        unit2 = 'dimensionless'

    if unit2.lower().strip(' ()') in dictionary['dimensionless']:
        return unit1
    if unit1.lower().strip(' ()') in dictionary['dimensionless']:
        if unit2.lower().strip(' ()') not in dictionary['dimensionless']:
            uBas, uPow = unitBasePower('1/' + unit2)
            return uBas+str(uPow)
        else:
            return unit1

    if unit1 != unit2 and convertible(unit1, unit2):
        return unitDivision(unit1, unit1)

    U1bas, U1pow = unitBasePower(unit1)
    U2bas, U2pow = unitBasePower(unit2)

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

    elif ('+' not in unit1 and '-' not in unit1 and '^' not in unit1) and (
            '+' not in unit2 and '-' not in unit2 and '^' not in unit2):
        if '*' in unit1 and unitBase(unit2) in map(unitBase, unit1.split('*')):
            result = ''
            for u in unit1.split('*'):
                if unit2 == u:
                    return '*'.join([u for u in unit1.split('*') if u != unit2])
                elif unitBase(unit2) == unitBase(u):
                    result = (result + '*' + unitDivision(u, unit2).strip('*')).strip('*')
                else:
                    result = (result + '*' + u).strip('*')
    else:
        for c in ['+','-','^']:  # '*','/'
            if c in unit1:
                unit1 = '('+unit1+')'
                break
        for c in ['+','-','^']:  # '*','/'
            if c in unit2:
                unit2 = '('+unit2+')'
                break
        result = unit1 + '/' + unit2

    return result
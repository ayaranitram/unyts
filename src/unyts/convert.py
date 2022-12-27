#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['converter', 'convertible', 'convert_unit']

from .database import unitsNetwork
from .dictionaries import dictionary, temperatureRatioConversions
from .searches import BFS, print_path
from .errors import NoConversionFoundError
import numpy as np
from functools import reduce


def _clean_print_conversion_path(print_conversion_path):
    if print_conversion_path is None:
        print_conversion_path = unitsNetwork.print
    elif type(print_conversion_path) is not bool:
        if type(print_conversion_path) in [int, float]:
            if print_conversion_path == 1:
                print_conversion_path = True
            else:
                print_conversion_path = False
        else:
            print_conversion_path = True
    return print_conversion_path


def convertible(from_unit, to_unit) -> bool:
    try:
        converter(1, from_unit, to_unit, False)
        return True
    except NoConversionFoundError:
        return False


def convert_unit(value, from_unit, to_unit, print_conversion_path=False):
    """
    returns the received value (integer, float, array, Series, DataFrame, etc)
    transformed from the units 'fromUnit' to the units 'toUnits.

    Parameters
    ----------
    value : int, float, array, Series, DataFrame, etc
        the value to be converted.
    from_unit : str
        the units of the provided value.
    to_unit : str
        the units to convert the value.
    print_conversion_path : bool, optional
        Set to True to show the path used for Conversion. The default is False.

    Returns
    -------
    converted_value : int, float, array, Series, DataFrame ...
        the converted value

    """
    print_conversion_path = _clean_print_conversion_path(print_conversion_path)

    try:
        conv = converter(value, from_unit, to_unit, print_conversion_path)
        if conv is not None:
            return conv
    except NoConversionFoundError:
        return None


def convertUnit_for_SimPandas(value, from_unit, to_unit, print_conversion_path=False):
    print_conversion_path = _clean_print_conversion_path(print_conversion_path)

    try:
        conv = converter(value, from_unit, to_unit, print_conversion_path)
        if conv is not None:
            return conv
        else:
            return value
    except NoConversionFoundError:
        return value


def _apply_conversion(value, conversion_path, print_conversion_path=False):
    if print_conversion_path:
        print("\n converting from '" + str(conversion_path[0]) + "' to '" + str(conversion_path[-1]) + "'\n  " +
              print_path(conversion_path))
    for conversion in range(len(conversion_path) - 1):
        value = unitsNetwork.convert(value, conversion_path[conversion], conversion_path[conversion + 1])
    return value


def _lambda_conversion(conversion_path, print_conversion_path=False):
    if print_conversion_path:
        print("\n converting from '" + str(conversion_path[0]) + "' to '" + str(conversion_path[-1]) + "'\n  " +
              print_path(conversion_path))
    big_lambda = []
    for i in range(len(conversion_path) - 1):
        big_lambda += [unitsNetwork.conversion(conversion_path[i], conversion_path[i + 1])]
    return lambda x: _lambda_loop(x, big_lambda[:])


def _lambda_loop(x, lambda_list):
    for L in lambda_list:
        x = L(x)
    return x


def _split_ratio(unit):
    unit_up, unit_down = unit.split('/')
    return unit_up.strip(), unit_down.strip()


def _split_product(unit):
    unit_a, unit_b = unit.split('*')
    return unit_a.strip(), unit_b.strip()


def _split_unit(unit):
    result = None
    for c in unit:
        if c in '*/':
            result.append(c)
        elif result is None:
            result = [c]
        elif result[-1] in '*/':
            result.append(c)
        else:
            result[-1] = result[-1] + c
    return result


def _get_pair_child(unit):
    # get the Unit node if the name received
    unit = unitsNetwork.get_node(unit) if type(unit) is str else unit

    # get pair of units children
    pair_child = list(filter(lambda u: '/' in u or '*' in u, [u.get_name() for u in unitsNetwork.children_of(unit)]))

    # if pair of units child is found, return the one with the shorter name
    if len(pair_child) > 0:
        pair_child = sorted(pair_child, key=len)[0]

    # if no children found at this level, look for children in next level
    else:
        for child in unitsNetwork.children_of(unit):
            pair_grandchild = list(
                filter(lambda u: '/' in u or '*' in u, [u.get_name() for u in unitsNetwork.children_of(child)]))
            if len(pair_grandchild) > 0:
                pair_child = sorted(pair_grandchild, key=len)[0]
                break

    if type(pair_child) is str:
        return pair_child


def _get_conversion(value, from_unit, to_unit, print_conversion_path=None, get_path=False):
    # specific cases for quick conversions
    # no conversion required if 'from' and 'to' units are the same units
    if from_unit == to_unit:
        return (lambda x: x) if value is None else value

    # no conversion required if 'from' and 'to' units are dates
    if from_unit in dictionary['date'] and to_unit in dictionary['date']:
        return (lambda x: x) if value is None else value

    # special case for Temperature ratios
    if '/' in from_unit and len(from_unit.split('/')) == 2 and from_unit.split('/')[0] in dictionary['Temperature'] \
            and '/' in to_unit and len(to_unit.split('/')) == 2 and to_unit.split('/')[0] in dictionary['Temperature']:
        t1, d1 = from_unit.split('/')
        t2, d2 = to_unit.split('/')
        num = temperatureRatioConversions[(t1, t2)]
        den = _get_conversion(1, d1, d2, print_conversion_path=print_conversion_path, get_path=get_path)
        if num is None or den is None:
            return None  # raise NoConversionFoundError("from '" + str(d1) + "' to '" + str(d2) + "'")
        return (lambda x: x * num / den) if value is None else (value * num / den)

    # from Dimensionless/None to some units or viceversa (to allow assign units to Dimensionless numbers)
    if from_unit is None or to_unit is None:
        return (lambda x: x) if value is None else value
    if (from_unit.lower() in dictionary['Dimensionless'] or to_unit.lower() in dictionary['Dimensionless']) and (
            from_unit is None or to_unit is None):
        return (lambda x: x) if value is None else value

    # from Dimensionless to Percentage or viceversa
    if (from_unit is None or from_unit.lower() in dictionary['Dimensionless']) and to_unit.lower() in dictionary[
        'Percentage']:
        return (lambda x: x * 100) if value is None else value * 100
    if from_unit.lower() in dictionary['Percentage'] and (
            to_unit is None or to_unit.lower() in dictionary['Dimensionless']):
        return (lambda x: x / 100) if value is None else value / 100

    # from Dimensionless to ratio of same units
    if from_unit.lower() in dictionary['Dimensionless'] and '/' in to_unit and len(to_unit.split('/')) == 2 and \
            to_unit.lower().split('/')[0].strip(' ()') == to_unit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    # from ratio of same units to Dimensionless
    if to_unit.lower() in dictionary['Dimensionless'] and '/' in from_unit and len(from_unit.split('/')) == 2 and \
            from_unit.lower().split('/')[0].strip(' ()') == from_unit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x) if value is None else value

    # if inverted ratios
    if ('/' in from_unit and len(from_unit.split('/')) == 2) and ('/' in to_unit and len(to_unit.split('/')) == 2) and (
            from_unit.split('/')[0].strip() == to_unit.split('/')[1].strip()) and (
            from_unit.split('/')[1].strip() == to_unit.split('/')[0].strip()):
        return (lambda x: 1 / x) if value is None else 1 / value

    # check if already solved and memorized
    if not get_path and (from_unit, to_unit) in unitsNetwork.memory:
        conversion_lambda = unitsNetwork.memory[(from_unit, to_unit)]
        return conversion_lambda if value is None else conversion_lambda(value)

    # check if path is alredy defined in network
    if unitsNetwork.has_node(from_unit) and unitsNetwork.has_node(to_unit):
        conversion_path = BFS(unitsNetwork, unitsNetwork.get_node(from_unit), unitsNetwork.get_node(to_unit))
    else:
        conversion_path = None

    # return Conversion if found in network
    if conversion_path is not None:
        unitsNetwork.memory[(from_unit, to_unit)] = _lambda_conversion(conversion_path, print_conversion_path=False)
        if get_path:
            return conversion_path
        return _apply_conversion(value, conversion_path, print_conversion_path) if value is not None else \
            unitsNetwork.memory[(from_unit, to_unit)]


def converter(value, from_unit, to_unit, print_conversion_path=None):
    """
    returns the received value (integer, float, array, series, dataframe, etc)
    transformed from the units 'from_unit' to the units 'to_units.
    """
    if hasattr(value, '__iter__') and type(value) is not np.array:
        value = np.array(value)

    print_conversion_path = _clean_print_conversion_path(print_conversion_path)

    # cleaning inputs
    ## strip off the parentesis, the string o
    if type(from_unit) is str and from_unit not in ('"', "'"):
        from_unit = from_unit.strip("( ')").strip('( ")').strip("'")
    else:
        from_unit = from_unit.strip("( )")
    if type(to_unit) is str and to_unit not in ('"', "'"):
        to_unit = to_unit.strip("( ')").strip('( ")').strip("'")
    else:
        to_unit = to_unit.strip("( )")

    # reset memory for this variable
    unitsNetwork.previous = []

    # try to convert
    conversion = _get_conversion(value, from_unit, to_unit,
                                 print_conversion_path=print_conversion_path)

    # if Conversion found
    if conversion is not None:
        return conversion

    # else, if Conversion path not found, start a new search part by part
    # check if pair from-to already visited
    if (from_unit, to_unit) in unitsNetwork.previous:
        allow_recursion = 0  # stop recursion here
    # append this pair to this search history
    unitsNetwork.previous.append((from_unit, to_unit))

    list_conversion = []
    split_from = _split_unit(from_unit)
    split_to = _split_unit(to_unit)
    used_to = []
    failed = False
    for f in range(len(split_from)):
        flag = False
        if split_from[f] in '*/':
            continue
        for t in range(len(split_to)):
            if t in used_to:
                continue
            if split_to[t] in '*/':
                continue
            conversion = _get_conversion(1, split_from[f], split_to[t],
                                         print_conversion_path=print_conversion_path,
                                         get_path=False)
            if conversion is not None:
                flag = True
                if (f > 0 and split_from[f - 1] == '/') or (t > 0 and split_to[t - 1] == '/'):
                    conversion = 1 / conversion
                list_conversion.append(conversion)
                used_to.append(t)
                break
        if not flag:
            failed = True
            break

    if list_conversion != [] and not failed:
        conversion_factor = reduce(lambda x, y: x * y, list_conversion)
        unitsNetwork.memory[(from_unit, to_unit)] = lambda x: x * conversion_factor
        return value * conversion_factor if value is not None else unitsNetwork.memory[(from_unit, to_unit)]

    # look for one to pair Conversion
    if ('/' in to_unit or '*' in to_unit) and ('/' not in from_unit and '*' not in from_unit):
        from_unit_child = _get_pair_child(from_unit)
        if from_unit_child is not None:
            base_conversion = _get_conversion(1, from_unit, from_unit_child)
            sep = '/' if '/' in from_unit_child else '*'
            from_num, from_den = from_unit_child.split(sep)
            sep = '/' if '/' in to_unit else '*'
            if len(to_unit.split(sep)) == 2:
                to_num, to_den = to_unit.split(sep)
            else:
                raise NotImplementedError("Conversion from single to triple or more not implemented.")
            numerator = _get_conversion(1, from_num, to_num, get_path=False)
            denominator = 1 / _get_conversion(1, from_den, to_den, get_path=False)
            if numerator is not None and denominator is not None:
                conversion_factor = base_conversion * numerator / denominator
                unitsNetwork.memory[(from_unit, to_unit)] = lambda x: x * conversion_factor
                return value * conversion_factor if value is not None else unitsNetwork.memory[(from_unit, to_unit)]

    # no Conversion found
    raise NoConversionFoundError("from '" + str(from_unit) + "' to '" + str(to_unit) + "'")

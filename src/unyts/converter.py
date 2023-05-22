#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.6'
__release__ = 20230522
__all__ = ['convert', 'convertible']

from .database import units_network
from .dictionaries import dictionary, temperatureRatioConversions, uncertain_names
from .searches import BFS, print_path
from .errors import NoConversionFoundError
from .parameters import unyts_parameters_, _get_density
from .helpers.unit_string_tools import split_unit as _split_unit, reduce_parentheses as _reduce_parentheses
from functools import reduce
import logging

try:
    import numpy as np
    from numpy import ndarray

    _numpy_ = True
except ModuleNotFoundError:
    _numpy_ = False
    logging.warning("Missing NumPy package, operations with `list` of values will fail.")
try:
    from pandas import Series, DataFrame

    _pandas_ = True
except ModuleNotFoundError:
    _pandas_ = False

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

if _numpy_ and _pandas_:
    numeric = (int, float, complex, ndarray, Series, DataFrame)
elif _numpy_:
    numeric = (int, float, complex, ndarray)
elif _pandas_:
    numeric = (int, float, complex, Series, DataFrame)
else:
    numeric = (int, float, complex)


def _str2lambda(string: str):
    if string == '/':
        return lambda x, y: x / y
    if string == '*':
        return lambda x, y: x * y


def _apply_conversion(value, conversion_path):
    if len(conversion_path) == 1 and conversion_path[0] == '1/':
        return 1 / value
    i = 0
    while i < len(conversion_path) - 1:
        this_step, next_step = conversion_path[i], conversion_path[i + 1]
        if type(this_step) is str:
            if len(this_step) == 1:
                if type(next_step) in (int, float, complex):
                    value = _str2lambda(this_step)(value, _apply_conversion(next_step, conversion_path[i + 2:]))
                else:
                    value = _str2lambda(this_step)(value, _apply_conversion(value, conversion_path[i + 1:]))
                break
            elif this_step == '1/':
                value = 1 / _apply_conversion(value, conversion_path[i + 1:])
                break
            else:
                raise ValueError("string operation in conversion_path must be '/' or '*'")
        elif type(this_step) in (int, float, complex):
            if type(next_step) is str:
                value = _str2lambda(next_step)(value, _apply_conversion(this_step, conversion_path[i + 2:]))
                break
            else:
                value = _apply_conversion(this_step, conversion_path[i + 1:])
                break
        elif type(next_step) is str:
            if len(next_step) == 1:
                if len(conversion_path) == i + 2:
                    further_step = conversion_path[i + 2]
                    if type(further_step) in (int, float, complex):
                        value = _str2lambda(next_step)(value, further_step)
                    else:
                        value = _str2lambda(next_step)(value, _apply_conversion(value, further_step))
                    break
                elif len(conversion_path) > i + 2:
                    further_step = conversion_path[i + 2]
                    if type(further_step) in (int, float, complex):
                        value = _str2lambda(next_step)(value, _apply_conversion(further_step, conversion_path[i + 3:]))
                    else:
                        value = _str2lambda(next_step)(value, _apply_conversion(value, further_step))
                    break
        else:
            value = units_network.convert(value, this_step, next_step)
        i += 1
    return value


def _lambda_conversion(conversion_path):
    big_lambda = [units_network.conversion(conversion_path[i], conversion_path[i + 1])
                  for i in range(len(conversion_path) - 1)]
    return lambda x: _lambda_loop(x, big_lambda[:])


def _lambda_loop(x, lambda_list):
    for lambda_i in lambda_list:
        x = lambda_i(x)
    return x


def _get_pair_child(unit: str):
    # get the Unit node if the name received
    unit = units_network.get_node(unit) if type(unit) is str else unit

    # get pair of units children
    pair_child = list(filter(lambda u: '/' in u or '*' in u, [u.get_name() for u in units_network.children_of(unit)]))

    # if pair of units child is found, return the one with the shorter name
    if len(pair_child) > 0:
        pair_child = sorted(pair_child, key=len)[0]
    # if no children found at this level, look for children in next level
    else:
        for child in units_network.children_of(unit):
            pair_grandchild = list(
                filter(lambda u: '/' in u or '*' in u, [u.get_name() for u in units_network.children_of(child)]))
            if len(pair_grandchild) > 0:
                pair_child = sorted(pair_grandchild, key=len)[0]
                break

    if type(pair_child) is str:
        return pair_child


def _get_conversion(value, from_unit, to_unit):
    # specific cases for quick conversions
    # no conversion required if 'from' and 'to' units are the same units
    if from_unit == to_unit:
        if value is None:
            return lambda x: x, [units_network.get_node(from_unit) if units_network.has_node(from_unit) else from_unit]
        else:
            return value, [units_network.get_node(from_unit) if units_network.has_node(from_unit) else from_unit]

    # no conversion required if 'from' and 'to' units are dates
    if from_unit in dictionary['Date'] and to_unit in dictionary['Date']:
        if value is None:
            return lambda x: x, [units_network.get_node(from_unit) if units_network.has_node(from_unit) else from_unit,
                                 units_network.get_node(to_unit) if units_network.has_node(to_unit) else to_unit]
        else:
            return value, [units_network.get_node(from_unit) if units_network.has_node(from_unit) else from_unit,
                           units_network.get_node(to_unit) if units_network.has_node(to_unit) else to_unit]

    # from None to some units or viceversa
    if from_unit is None or to_unit is None:
        return (lambda x: x, []) if value is None else (value, [])

    # from Dimensionless to Percentage or viceversa
    if (from_unit.lower() in dictionary['Dimensionless']) and to_unit.lower() in dictionary['Percentage']:
        return (lambda x: x * 100, ['*', 100]) if value is None else (value * 100, ['*', 100])
    if from_unit.lower() in dictionary['Percentage'] and to_unit.lower() in dictionary['Dimensionless']:
        return (lambda x: x / 100, ['/', 100]) if value is None else (value / 100, ['/', 100])

    # from Dimensionless to some units (not ratios), to allow assign units to Dimensionless numbers
    if from_unit.lower() in dictionary['Dimensionless'] and '/' not in to_unit:
        return (lambda x: x, []) if value is None else (value, [])

    # special case for Temperature ratios
    if '/' in from_unit and len(from_unit.split('/')) == 2 and from_unit.split('/')[0] in dictionary['Temperature'] \
            and '/' in to_unit and len(to_unit.split('/')) == 2 and to_unit.split('/')[0] in dictionary['Temperature']:
        t1, d1 = from_unit.split('/')
        t2, d2 = to_unit.split('/')
        num = temperatureRatioConversions[(t1, t2)]
        den, den_path = _get_conversion(1, d1, d2)
        if num is None or den is None:
            if unyts_parameters_.raise_error_:
                raise NoConversionFoundError("from '" + str(d1) + "' to '" + str(d2) + "'")
            else:
                return None, None
        den_path = [1] + den_path
        if value is None:
            return lambda x: x * num / den, ['*', num, '/'] + den_path
        else:
            return value * num / den, ['*', num, '/'] + den_path

    # from Dimensionless to ratio of same units
    if from_unit.lower() in dictionary['Dimensionless'] and '/' in to_unit and len(to_unit.split('/')) == 2 and \
            to_unit.lower().split('/')[0].strip(' ()') == to_unit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x, []) if value is None else (value, [])

    # from ratio of same units to Dimensionless
    if to_unit.lower() in dictionary['Dimensionless'] and '/' in from_unit and len(from_unit.split('/')) == 2 and \
            from_unit.lower().split('/')[0].strip(' ()') == from_unit.lower().split('/')[1].strip(' ()'):
        return (lambda x: x, []) if value is None else (value, [])

    # if inverted ratios
    if ('/' in from_unit and len(from_unit.split('/')) == 2) and ('/' in to_unit and len(to_unit.split('/')) == 2) and (
            from_unit.split('/')[0].strip() == to_unit.split('/')[1].strip()) and (
            from_unit.split('/')[1].strip() == to_unit.split('/')[0].strip()):
        if value is None:
            return lambda x: 1 / x, ['1/']
        else:
            return 1 / value, ['1/']

    # check if already solved and memorized
    if (from_unit, to_unit) in units_network.memory:
        conversion_lambda, conversion_path = units_network.memory[(from_unit, to_unit)]
        return (conversion_lambda, conversion_path) if (conversion_lambda is None or value is None) \
            else (conversion_lambda(value), conversion_path)

    # check if path is already defined in network
    if units_network.has_node(from_unit) and units_network.has_node(to_unit):
        conversion_path = BFS(units_network,
                              units_network.get_node(from_unit),
                              units_network.get_node(to_unit),
                              unyts_parameters_.verbose_)
    else:
        conversion_path = None

    # return Conversion if found in network
    if conversion_path is not None:
        units_network.memory[(from_unit, to_unit)] = (_lambda_conversion(conversion_path), conversion_path)
        if value is None:
            return units_network.memory[(from_unit, to_unit)]
        else:
            return _apply_conversion(value, conversion_path), conversion_path
    else:
        return None, None


def _converter(value, from_unit, to_unit):
    """
    returns the received value (integer, float, array, series, dataframe, etc)
    transformed from the units 'from_unit' to the units 'to_units'
    as well as conversion path.
    """
    # reset memory for this variable
    units_network.previous = []

    # try to convert
    conv, conv_path = _get_conversion(value, from_unit, to_unit)

    # if Conversion found
    if conv is not None:
        return conv, conv_path

    units_network.previous.append((from_unit, to_unit))

    list_conversion = []
    list_conversion_path = []
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
            conv, conv_path = _get_conversion(1, split_from[f], split_to[t])
            if conv is not None:
                flag = True
                if len(list_conversion_path) > 0:
                    conv_path = [1] + conv_path
                if (f > 0 and split_from[f - 1] == '/') or (t > 0 and split_to[t - 1] == '/'):
                    conv = 1 / conv
                    conv_path = ['/'] + conv_path
                list_conversion.append(conv)
                list_conversion_path.append(conv_path)
                used_to.append(t)
                break
        if not flag:
            failed = True
            break

    if len(list_conversion) > 0 and not failed:
        conversion_factor = reduce(lambda x, y: x * y, list_conversion)
        conversion_path = [node for path in list_conversion_path for node in path]
        units_network.memory[(from_unit, to_unit)] = lambda x: x * conversion_factor, conversion_path
        if value is None:
            return units_network.memory[(from_unit, to_unit)]
        else:
            return value * conversion_factor, conversion_path

    # look for one to pair conversion path
    if ('/' in to_unit or '*' in to_unit) and ('/' not in from_unit and '*' not in from_unit):
        from_unit_child = _get_pair_child(from_unit)
        if from_unit_child is not None:
            base_conversion, base_conversion_path = _get_conversion(None, from_unit, from_unit_child)
            pair_conversion, pair_conversion_path = _converter(None, from_unit_child, to_unit)
            if pair_conversion is not None and base_conversion is not None:
                conversion_path = base_conversion_path + pair_conversion_path
                conversion = lambda x: pair_conversion(base_conversion(x))
                units_network.memory[(from_unit, to_unit)] = conversion, conversion_path
                if value is None:
                    return units_network.memory[(from_unit, to_unit)]
                else:
                    return conversion(value), conversion_path

    # look for pair to one conversion path
    elif ('/' in from_unit or '*' in from_unit) and ('/' not in to_unit or '*' not in to_unit):
        to_unit_child = _get_pair_child(to_unit)
        if to_unit_child is not None:
            final_conversion, final_conversion_path = _get_conversion(None, to_unit_child, to_unit)
            pair_conversion, pair_conversion_path = _converter(None, from_unit, to_unit_child)
            if pair_conversion is not None and final_conversion is not None:
                conversion_path = pair_conversion_path + final_conversion_path
                conversion = lambda x: final_conversion(pair_conversion(x))
                units_network.memory[(from_unit, to_unit)] = conversion, conversion_path
                if value is None:
                    return units_network.memory[(from_unit, to_unit)]
                else:
                    return conversion(value), conversion_path

    units_network.memory[(from_unit, to_unit)] = None, None
    return None, None


def _clean_print_conversion_path(print_conversion_path: bool = None) -> bool:
    return unyts_parameters_.print_path_ if print_conversion_path is None else bool(print_conversion_path)


def _clean_verbose(verbose) -> bool:
    return unyts_parameters_.verbose_ if verbose is None else bool(verbose)


def convertible(from_unit: str, to_unit: str) -> bool:
    from unyts.unit_class import Unit
    if isinstance(from_unit, Unit):
        from_unit = from_unit.get_unit()
    if isinstance(to_unit, Unit):
        to_unit = to_unit.get_unit()

    try:
        conv, conv_path = _converter(1, from_unit, to_unit)
        return False if conv is None else True
    except NoConversionFoundError:
        return False


def convert(value: numeric, from_unit: str, to_unit: str, print_conversion_path: bool = None):
    """
    returns the received value (integer, float, array, Series, DataFrame, etc)
    transformed from the units 'from_unit' to the units 'to_units'.

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
    lambda_conversion : lambda
        if input value is None, or
    converted_value : int, float, array, Series, DataFrame ...
        the converted value if input value is not None
    """
    from unyts.unit_class import Unit
    # cleaning inputs
    if _numpy_ and hasattr(value, '__iter__') and type(value) is not np.array:
        value = np.array(value)
    if isinstance(value, Unit):
        value = value.get_value()
    if value is not None and not isinstance(value, numeric):
        raise ValueError("value must be numeric.")
    if type(value) in [list, tuple]:
        raise TypeError("`value` can not be a list or tuple if NumPy is not installed.")
    if isinstance(from_unit, Unit):
        from_unit = from_unit.get_unit()
    if isinstance(to_unit, Unit):
        to_unit = to_unit.get_unit()
    print_conversion_path = _clean_print_conversion_path(print_conversion_path)

    if type(from_unit) is str and from_unit not in ('"', "'"):
        from_unit = from_unit.strip("( ')").strip('( ")').strip("'")
    elif type(from_unit) is str:
        from_unit = from_unit.strip("( )")
    elif from_unit is None:
        from_unit = 'None'
    else:
        raise TypeError(f"'from_unit' must be string, not {type(from_unit)}, like {from_unit}")
    if type(to_unit) is str and to_unit not in ('"', "'"):
        to_unit = to_unit.strip("( ')").strip('( ")').strip("'")
    elif type(to_unit) is str:
        to_unit = to_unit.strip("( )")
    elif to_unit is None:
        to_unit = 'None'
    else:
        raise TypeError(f"'to_unit' must be string, not {type(to_unit)}, like {to_unit}")

    if unyts_parameters_.reduce_parentheses_:
        from_unit = _reduce_parentheses(from_unit)
        to_unit = _reduce_parentheses(to_unit)

    # density factor, in case of conversion from volume to mass or mass to volume
    if from_unit not in uncertain_names and to_unit not in uncertain_names and \
            from_unit in dictionary['Volume'] and to_unit in dictionary['Weight']:
        density = _get_density()
        conv1, conv_path1 = _converter(value, from_unit, 'cc')
        conv2, conv_path2 = _converter(value, 'g', to_unit)
        if value is None:
            conv = lambda x: conv2(conv1(x) * density)
        else:
            conv = conv1 * density * conv2
        conv_path = conv_path1 + ['*', density, '*'] + conv_path2
    elif from_unit not in uncertain_names and to_unit not in uncertain_names and \
            to_unit in dictionary['Volume'] and from_unit in dictionary['Weight']:
        density = _get_density()
        conv1, conv_path1 = _converter(value, from_unit, 'g')
        conv2, conv_path2 = _converter(value, 'cc', to_unit)
        if value is None:
            conv = lambda x: conv2(conv1(x) / density)
        else:
            conv = conv1 / density * conv2
        conv_path = conv_path1 + ['/', density, '*'] + conv_path2
    else:  # regular conversion
        conv, conv_path = _converter(value, from_unit, to_unit)

    if conv is None:
        if unyts_parameters_.raise_error_:
            raise NoConversionFoundError("from '" + str(from_unit) + "' to '" + str(to_unit) + "'")
        else:
            return None

    if print_conversion_path:
        logging.info("converting from '" + str(from_unit) + "' to '" + str(to_unit) + ":\n" +
                     str(print_path(conv_path)))

    return conv


def convert_for_SimPandas(value: numeric, from_unit: str, to_unit: str, print_conversion_path: bool = False):
    conv = None
    print_conversion_path = bool(print_conversion_path)
    if convertible(from_unit, to_unit):
        conv, conv_path = _converter(value, from_unit, to_unit)
    if print_conversion_path and conv is not None:
        logging.info("converting from '" + str(from_unit) + "' to '" + str(to_unit) + ":\n" +
                     str(print_path(conv_path)))
    elif print_conversion_path and conv is not None:
        logging.warning("conversion not found, returning original values.")
    return value if conv is None else conv

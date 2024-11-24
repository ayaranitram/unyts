#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:57:27 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.8.6'
__release__ = 20241124
__all__ = ['convert', 'convertible']

from .database import units_network
from .dictionaries import dictionary, temperatureRatioConversions, uncertain_names
from .Empty import Empty, str_Empty
from .searches import BFS, lean_BFS, DFS, hybrid_BFS, print_path
from .errors import NoConversionFoundError
from .parameters import unyts_parameters_, _get_density
from .helpers.unit_string_tools import split_unit as _split_unit, reduce_parentheses as _reduce_parentheses
from functools import reduce
from typing import Union
from sys import getrecursionlimit
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
    _numeric = (int, float, complex, ndarray, Series, DataFrame)
    numeric = Union[int, float, complex, ndarray, Series, DataFrame]
elif _numpy_:
    _numeric = (int, float, complex, ndarray)
    numeric = Union[int, float, complex, ndarray]
elif _pandas_:
    _numeric = (int, float, complex, Series, DataFrame)
    numeric = Union[int, float, complex, Series, DataFrame]
else:
    _numeric = (int, float, complex)
    numeric = Union[int, float, complex]


def _str2lambda(string: str):
    """
    Returns a lambda with a multiplication or division operation, depending on the received string.

    Parameters
    ----------
    string: str

    Returns
    -------
    lambda
    """
    if string == '/':
        return lambda x, y: x / y
    if string == '*':
        return lambda x, y: x * y


def _apply_conversion(value, conversion_path):
    """
    Helper function to apply the functions stated in the `conversion_path`.
    Parameters
    ----------
    value: numeric (int, float, NumPy.array, ...)
        the value(s) to apply the conversion
    conversion_path: list
        conversion_path provided by _get_conversion()

    Returns
    -------
        numeric (int, float, NumPy.array, ...)
    """
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
    """
    Helper function to make a lambda applying in sequence all the conversions listed in the conversion_path.

    Parameters
    ----------
    conversion_path: list
        sequence of the conversions to be applied
    Returns
    -------
    conversion_lambda: lambda
        to apply the conversion path
    """
    big_lambda = [units_network.conversion(conversion_path[i], conversion_path[i + 1])
                  for i in range(len(conversion_path) - 1)]
    return lambda x: _lambda_loop(x, big_lambda[:])


def _lambda_loop(x, lambda_list):
    """
    Helper function to apply lambda functions in sequence.

    Parameters
    ----------
    x: numeric
        the value to apply the conversion sequence
    lambda_list : list
        a list of the conversions that should be applied in sequence

    Returns
    -------
    lambda_sequence : lambda
        all the lambdas in the list applied in sequence
    """
    for lambda_i in lambda_list:
        x = lambda_i(x)
    return x


def _get_pair_child(unit: str):
    """
    Returns the following child of a unit node.
    Parameters
    ----------
    unit: str

    Returns
    -------
        unit_node
    """
    # get the Unit node if the name received is string
    unit = units_network.get_node(unit) if type(unit) is str else unit

    # get a pair of units children
    pair_child = list(filter(lambda u: '/' in u or '*' in u, [u.get_name() for u in units_network.children_of(unit)]))

    # if a pair of units child is found, return the one with the shorter name
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


def _get_recursion_limit(recursion=None):
    if recursion is None:
        recursion = min(getrecursionlimit() - 15, unyts_parameters_.max_recursion_)
    elif recursion > 1:
        recursion = min(getrecursionlimit() - 15, recursion) - 1
    elif recursion <= 0:
        recursion = -1
    else:
        recursion -= 1
    return recursion


def _get_conversion(value, from_unit, to_unit, recursion=None, use_cache:bool=None):
    """
    Helper function to handle looking for the conversion factor of special cases and through the units network.

    Parameters
    ----------
    value: numeric or None
    from_unit: str
    to_unit: str
    recursion: int
        The limit of recursive calls to this function
    use_cache: bool
        Set to False to ignore searches in memory, and repeat the search.

    Returns
    -------
        (conversion, conversion_path)

    """
    # get and set recursion limit
    recursion = _get_recursion_limit(recursion)
    if unyts_parameters_.verbose_ and unyts_parameters_.verbose_details_ >= 2:
        logging.info(f"_get_conversion: {recursion} remaining recursions, converting from {from_unit} to {to_unit}")
    if recursion < 0:
        return None, None


    # check if already solved and memorized
    use_cache = unyts_parameters_.cache_ if use_cache is None else use_cache
    if use_cache and (from_unit, to_unit) in units_network.memory:
        conversion_lambda, conversion_path = units_network.memory[(from_unit, to_unit)]
        return (conversion_lambda, conversion_path) if (conversion_lambda is None or value is None) \
            else (conversion_lambda(value), conversion_path)

    ## specific cases for quick conversions ##
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

    # from None to some units or vice-versa
    if from_unit is None or to_unit is None:
        return (lambda x: x, []) if value is None else (value, [])

    # from Dimensionless to Percentage or vice-versa
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
        den, den_path = _get_conversion(1, d1, d2, recursion=recursion, use_cache=use_cache)
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

    # check if path is already defined in network
    conversion_path = _search_network(from_unit, to_unit)
    # return Conversion if found in network
    if conversion_path is not None:
        units_network.memory[(from_unit, to_unit)] = (_lambda_conversion(conversion_path), conversion_path)
        if value is None:
            return units_network.memory[(from_unit, to_unit)]
        else:
            return _apply_conversion(value, conversion_path), conversion_path
    else:
        return None, None
    

def generations_until_common(start, end, verbose=False, max_generations_screening=25) -> list:
    """
    Finds the number of generations requiered to get a common unit between `start` and `end`, 
    where `start` and `end` are nodes in the graph network.
    Returns a smaller number of generations to connect `start` to `end` in graph.

    Parameters
    ----------
    start: node
    end: node
    verbose: bool
        to print or not print messages.
    Returns
    -------
    shortest_path: list
    """
    from unyts.converter import _get_descendants
    max_generations_screening = unyts_parameters_.generations_limit() if max_generations_screening is None else max_generations_screening
    generations = 0
    selection = set()
    start = start.get_name() if hasattr(start, 'get_name') else start
    end = end.get_name() if hasattr(end, 'get_name') else end
    while len(selection) == 0 and generations < max_generations_screening:
        generations += 1
        start_descendants = _get_descendants(start, generations)
        end_descendants = _get_descendants(end, generations)
        selection = start_descendants.intersection(end_descendants)
    return generations if len(selection) > 0 else (np.inf if _numpy_ else 9999)


def _get_descendants(unit:str, generations=None, get_combinations=True):
    generations = unyts_parameters_.max_generations_ if generations is None else generations
    if generations == 0:
        return {unit}
    children, children_split = set(), set()
    unit_num, unit_den = None, None
    if units_network.has_node(unit):
        children = {unit}
        for g in range(generations):
            children = children.union({each for k, v in units_network.get_edges_str().items() for each in v if k in children})

    if get_combinations:
        for s in '/*':
            if s in unit and len(unit.split(s)) == 2:
                unit_num, unit_den = unit.split(s)
                break
        if unit_num is not None and unit_den is not None:
            children_num = _get_descendants(unit_num, generations)
            children_den = _get_descendants(unit_den, generations)
            children_split = {f"{str(num)}/{str(den)}"
                              for num in {unit_num}.union(children_num)
                              for den in {unit_den}.union(children_den)
                              if f"{str(num)}/{str(den)}" != unit}
        descendants = children.union(children_split)
    else:
        descendants = children
    return {unit}.union(descendants)


def _ratio_conversion_including_children(from_unit, to_unit, recursion=None, max_paths=12, use_cache:bool=None):
    """
    helper function of _converter function
    
    _pair_conversion_including_children will extend the search looking recursively 
    for conversion from from_unit chidren to to_unit children.
    
    the children of from_unit and to_unit are created as the ratio of combined children from 
    the numerator of the parent unit and the children of the denominator unit

    Parameters
    ----------
    from_unit : str
        unit string
    to_unit : str
        unit string
    recursion : int, optional
        limit of recursion allowed.

    Returns
    -------
    tuple
        (conversion, conversion_path)

    """
    # calculate the descendants of from_unit
    from_family = _get_descendants(from_unit)

    # calculate the descendants of to_unit
    to_family = _get_descendants(to_unit)

    # keep only intersection between families
    common = from_family.intersection(to_family)
    
    total_generations = lambda u: generations_until_common(from_unit, u) + generations_until_common(u, to_unit)
    from_to_generations = [total_generations(u) for u in common]
    min_generations = min(from_to_generations)
    common_sorted = {child: gens for gens, child in sorted(zip(from_to_generations, common))}

    # look for conversion between children  
    conversion, conversion_path = None, None
    path, shortest_path = 0, 9999
    for child in common_sorted:
        if conversion_path is not None and common_sorted[child] > min_generations:
            break
        from_child_conversion, from_child_conversion_path = _converter(None, from_unit, child, recursion=recursion, use_cache=use_cache)
        child_to_conversion, child_to_conversion_path = _converter(None, child, to_unit, recursion=recursion, use_cache=use_cache)
        if from_child_conversion is not None and child_to_conversion is not None:
            this_path_len = len([step for step in (from_child_conversion_path + child_to_conversion_path) if step != '1/'])
            if this_path_len < shortest_path:
                conversion_path = from_child_conversion_path + child_to_conversion_path
                conversion = lambda x: child_to_conversion(from_child_conversion(x))
                shortest_path = this_path_len
            if path == max_paths:
                break
        path += 1
    return conversion, conversion_path
    
    
def _converter(value, from_unit, to_unit, recursion=None, use_cache:bool=None):
    """
    Transform the received value (integer, float, array, series, frame, ...)
    from the units `from_unit` to the units `to_units` and report the conversion path used.

    Parameters
    ----------
    value: numeric or None
    from_unit: str
    to_unit: str
    recursion: int
        Limit the number of recursive calls to this function
    use_cache: bool
        Set to False to ignore cached searches, and repeat the search.


    Returns
    -------
        (conversion, conversion_path)
    """
    # avoid infinite looping, do not repeat searches
    if (from_unit, to_unit) in units_network.previous:
        return None, None
    
    # get and set recursion limit
    recursion = _get_recursion_limit(recursion)
    if unyts_parameters_.verbose_:
        logging.info(f"_converter: {recursion} remaining recursions, converting from {from_unit} to {to_unit}")
    if recursion < 0:
        return None, None

    # try to convert
    if unyts_parameters_.verbose_:
        logging.info(f"_converter: {recursion} remaining recursions, attempting direct conversion")
    conv, conv_path = _get_conversion(value, from_unit, to_unit, recursion=recursion, use_cache=use_cache)
    # if Conversion found
    if conv is not None:
        return conv, conv_path
    
    units_network.previous.append((from_unit, to_unit))
   
    # look for conversions of parts in ratio or product units
    if unyts_parameters_.verbose_:
        logging.info(f"_converter: {recursion} remaining recursions, attempting to convert ratio or product of units.")
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
            conv, conv_path = _get_conversion(1, split_from[f], split_to[t], recursion=recursion, use_cache=use_cache)
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

    # look for one-to-pair conversion path
    if ('/' in to_unit or '*' in to_unit) and ('/' not in from_unit and '*' not in from_unit):
        if unyts_parameters_.verbose_:
            logging.info(f"_converter: {recursion} remaining recursions, looking for one-to-pair conversion path")
        from_unit_child = _get_pair_child(from_unit)
        if from_unit_child is not None:
            base_conversion, base_conversion_path = _converter(None, from_unit, from_unit_child, recursion=recursion, use_cache=use_cache)
            pair_conversion, pair_conversion_path = _converter(None, from_unit_child, to_unit, recursion=recursion, use_cache=use_cache)
            if pair_conversion is not None and base_conversion is not None:
                conversion_path = base_conversion_path + pair_conversion_path
                conversion = lambda x: pair_conversion(base_conversion(x))
                units_network.memory[(from_unit, to_unit)] = conversion, conversion_path
                if value is None:
                    return units_network.memory[(from_unit, to_unit)]
                else:
                    return conversion(value), conversion_path

    # look for pair-to-one conversion path
    elif ('/' in from_unit or '*' in from_unit) and ('/' not in to_unit and '*' not in to_unit):
        if unyts_parameters_.verbose_:
            logging.info(f"_converter: {recursion} remaining recursions, looking for pair-to-one conversion path")
        to_unit_child = _get_pair_child(to_unit)
        if to_unit_child is not None:
            final_conversion, final_conversion_path = _converter(None, to_unit_child, to_unit, recursion=recursion, use_cache=use_cache)
            pair_conversion, pair_conversion_path = _converter(None, from_unit, to_unit_child, recursion=recursion, use_cache=use_cache)
            if pair_conversion is not None and final_conversion is not None:
                conversion_path = pair_conversion_path + final_conversion_path
                conversion = lambda x: final_conversion(pair_conversion(x))
                units_network.memory[(from_unit, to_unit)] = conversion, conversion_path
                if value is None:
                    return units_network.memory[(from_unit, to_unit)]
                else:
                    return conversion(value), conversion_path

    # look for pair to pair conversion path considering children
    if ('/' in from_unit) and ('/' in to_unit) and len(from_unit.split('/')) == 2 and len(to_unit.split('/')) == 2:
        if unyts_parameters_.verbose_:
            logging.info(f"_converter: {recursion} remaining recursions, looking for pair-to-pair conversion path considering children")
        conversion, conversion_path = _ratio_conversion_including_children(from_unit, to_unit, recursion=recursion)
        if conversion is not None:        
            units_network.memory[(from_unit, to_unit)] = conversion, conversion_path
            if value is None:
                return units_network.memory[(from_unit, to_unit)]
            else:
                return conversion(value), conversion_path

    if unyts_parameters_.verbose_:
        logging.error(f"_converter: {recursion} remaining recursions, no conversion found")
    units_network.memory[(from_unit, to_unit)] = None, None
    return None, None


def _clean_input(value: numeric, from_unit: str, to_unit: str_Empty) -> (numeric, str, str):
    """
    Helper function to preprocess the input parameters from the user
    Parameters
    ----------
    value: numeric, Unit or None
    from_unit: str, Unit or None
    to_unit: str, Unit, None or Empty

    Returns
    -------
        value: numeric
        from_unit: str
        to_unit: str
    """
    from unyts.unit_class import Unit

    if isinstance(value, Unit):
        if to_unit is Empty or to_unit == 'Empty':
            from_unit, to_unit = value.unit, from_unit
        value = value.get_value()
    if _numpy_ and hasattr(value, '__iter__') and type(value) is not np.array:
        value = np.array(value)
    elif not _numpy_ and type(value) in [list, tuple]:
        raise TypeError("Can't operate with list or tuple without NumPy. `value` can not be a list or tuple.")
    if value is not None and not isinstance(value, _numeric):
        raise ValueError("value must be numeric.")
    if isinstance(from_unit, Unit):
        from_unit = from_unit.get_unit()
    if isinstance(to_unit, Unit):
        to_unit = to_unit.get_unit()

    if isinstance(from_unit, str) and from_unit not in ('"', "'"):
        from_unit = from_unit.strip("( ')").strip('( ")').strip("'")
    elif isinstance(from_unit, str):
        from_unit = from_unit.strip("( )")
    elif from_unit is None:
        from_unit = 'None'
    elif _numpy_ and isinstance(from_unit, float) and np.isnan(from_unit):
        from_unit = 'None'
    else:
        raise TypeError(f"'from_unit' must be string, not {type(from_unit)}, like {from_unit}")

    if to_unit is Empty or to_unit == 'Empty':
        raise TypeError("convert() missing 1 required positional argument: 'to_unit'")
    if isinstance(to_unit, str) and to_unit not in ('"', "'"):
        to_unit = to_unit.strip("( ')").strip('( ")').strip("'")
    elif isinstance(to_unit, str):
        to_unit = to_unit.strip("( )")
    elif to_unit is None:
        to_unit = 'None'
    elif _numpy_ and isinstance(to_unit, float) and np.isnan(to_unit):
        to_unit = 'None'
    else:
        raise TypeError(f"'to_unit' must be string, not {type(to_unit)}, like {to_unit}")

    if unyts_parameters_.reduce_parentheses_:
        from_unit = _reduce_parentheses(from_unit)
        to_unit = _reduce_parentheses(to_unit)

    return value, from_unit, to_unit


def _clean_print_conversion_path(print_conversion_path: bool = None) -> bool:
    return unyts_parameters_.print_path_ if print_conversion_path is None else bool(print_conversion_path)


def _clean_verbose(verbose) -> bool:
    return unyts_parameters_.verbose_ if verbose is None else bool(verbose)


def _density_conversion(value: numeric, from_unit: str, to_unit: str, use_cache:bool=None):
    """
    Helper function to deal with conversion between weight and volume, using density.

    Parameters
    ----------
    value: numeric
    from_unit: str
    to_unit: str
    use_cache: bool

    Returns
    -------
    (conv, conv_path): (numeric or lambda, list) or (None, None)
        a conversion and the conversion path, if found.
    """
    if from_unit not in uncertain_names and to_unit not in uncertain_names and \
            from_unit in dictionary['Volume'] and to_unit in dictionary['Weight']:
        density = _get_density()
        this_units_density, _ = _converter(density, 'g/cm3', f"{to_unit}/{from_unit}", use_cache=use_cache)
        if value is None:
            conv = lambda x: x * this_units_density
        else:
            conv = value * this_units_density
        conv_path = ['*', this_units_density]
    elif from_unit not in uncertain_names and to_unit not in uncertain_names and \
            to_unit in dictionary['Volume'] and from_unit in dictionary['Weight']:
        density = _get_density()
        this_units_density = _converter(density, 'g/cm3', f"{from_unit}/{to_unit}", use_cache=use_cache)
        if value is None:
            conv = lambda x: x / this_units_density
        else:
            conv = value / this_units_density
        conv_path = ['/', this_units_density]
    else:
        conv, conv_path = None, None

    return conv, conv_path


def _search_network(from_unit, to_unit, algorithm:str=None):
    """
    Searches for a path from `from_units` through the units network to `to_units`.

    Parameters
    ----------
    from_unit: str
        the starting point of the search.
    to_unit: str
        the target to be found in the network.
    algorithm: str
        the algorithm to use for searching the network, the implemented alternatives are:
        - 'BFS': Breadth-First Search algorithm, will return the shortest path searching through the entire network one level at a time.
        - 'lean_BFS': will return the shortest path searching through a slimmed network of preselected nodes.
        - 'DFS': Depth-First Search algorithm, will return the first found path searching through the network one branch at a time.
        - 'hybrid_BFS': launch together BFS and lean_BFS searches, and returns the first valid result.
    Returns
    -------
        conversion_path: list
            the list of steps to go from `from_unit` until `to_unit`.
    """
    if algorithm is None:
        algorithm = unyts_parameters_.algorithm_
    if units_network.has_node(from_unit) and units_network.has_node(to_unit):
        if algorithm == 'BFS':
            conversion_path = BFS(units_network,
                                  units_network.get_node(from_unit),
                                  units_network.get_node(to_unit),
                                  verbose=unyts_parameters_.verbose_ and unyts_parameters_.verbose_details_ > 1)
        elif algorithm == 'lean_BFS':
            conversion_path = lean_BFS(units_network, units_network.get_node(from_unit),
                                       units_network.get_node(to_unit),
                                       verbose=unyts_parameters_.verbose_,
                                       max_generations_screening=unyts_parameters_.generations_limit())
        elif algorithm == 'DFS':
            conversion_path = DFS(units_network, units_network.get_node(from_unit),
                                  units_network.get_node(to_unit),
                                  verbose=unyts_parameters_.verbose_ and unyts_parameters_.verbose_details_ > 1,
                                  branch_depht=unyts_parameters_.generations_limit())
        elif algorithm == 'hybrid_BFS':
            conversion_path = hybrid_BFS(units_network, units_network.get_node(from_unit),
                                         units_network.get_node(to_unit), verbose=unyts_parameters_.verbose_,
                                         max_generations_screening=unyts_parameters_.generations_limit())
        else:
            raise NotImplementedError("other search algorithms different from BFS and DFS are not yet implemented.")
    else:
        conversion_path = None
    return conversion_path


def convertible(from_unit: str, to_unit: str, use_cache:bool=None) -> bool:
    """
    Returns True if a conversion path from `from_unit` to `to_unit` is found, otherwise returns True.

    Parameters.
    ----------
    from_unit: str, Unit or None
    to_unit: str, Unit or None
    use_cache: bool
        Set to False to ignore cached searches, and repeat the search.

    Returns
    -------
        bool
    """
    from unyts.unit_class import Unit
    if isinstance(from_unit, Unit):
        from_unit = from_unit.get_unit()
    if isinstance(to_unit, Unit):
        to_unit = to_unit.get_unit()

    try:
        conv, conv_path = _converter(1, from_unit, to_unit, use_cache=use_cache)
        return False if conv is None else True
    except NoConversionFoundError:
        return False


def convert(value: numeric, from_unit: str, to_unit: str_Empty = Empty,
            print_conversion_path: bool = None, use_cache:bool=None):
    """
    Converts the received value (integer, float, array, Series, Frame, ...) from the units 'from_unit' to the units 'to_units'.

    Parameters
    ----------
    value : numeric (int, float, NumPy.array, Series, DataFrame, ...)
        the value to be converted.
    from_unit : str, Unit or None
        the units of the provided value.
    to_unit : str, Unit, None or Empty (the Empty class or the string "Empty")
        the units to convert the value.
    print_conversion_path : bool, optional
        Set to True to show the path used for Conversion. The default is False.
    use_cache: bool
        Set to False to ignore cached searches, and repeat the search.

    Returns
    -------
    lambda_conversion : lambda
        if input value is None, or
    converted_value : int, float, array, Series, DataFrame ...
        the converted value if input value is not None
    """
    if unyts_parameters_.verbose_:
        logging.info("convert: STARTING...")
    # cleaning inputs
    value, from_unit, to_unit = _clean_input(value, from_unit, to_unit)
    print_conversion_path = _clean_print_conversion_path(print_conversion_path)
    # reset previous memory for this variable
    units_network.previous = []

    # density factor, in case of conversion from volume to mass or mass to volume
    conv, conv_path = _density_conversion(value, from_unit, to_unit, use_cache=use_cache)

    if conv is None:
        # regular conversion
        conv, conv_path = _converter(value, from_unit, to_unit, use_cache=use_cache)

    if conv is None:
        if unyts_parameters_.raise_error_:
            raise NoConversionFoundError(f"from '{from_unit}' to '{to_unit}'")
        else:
            return None

    unyts_parameters_.last_path_str = print_path(conv_path)
    if print_conversion_path:
        logging.info(f"converting from '{from_unit}' to '{to_unit}':\n {unyts_parameters_.last_path_str}")

    return conv


def convert_for_SimPandas(value: numeric, from_unit: str, to_unit: str,
                          print_conversion_path:bool=False, use_cache:bool=None):
    """
    Particular implementation of `convert` function, specially set for SimDataFrames and SimSeries.
    If possible to convert the units, the returns the received value (integer, float, array, Series, Frame, ...)
    transformed from the units 'from_unit' to the units 'to_units'.
    If not possible to convert, return the original `value`.

    Parameters
    ----------
    value : Series, DataFrame
        the value to be converted.
    from_unit : str
        the units of the provided value.
    to_unit : str
        the units to convert the value.
    print_conversion_path : bool, optional
        Set to True to show the path used for Conversion. The default is False.
    use_cache: bool
        Set to False to ignore cached searches, and repeat the search.

    Returns
    -------
    converted_value : Series, DataFrame
        the converted value if input value is not None
    """
    conv = None
    print_conversion_path = bool(print_conversion_path)
    if convertible(from_unit, to_unit):
        conv, conv_path = _converter(value, from_unit, to_unit, use_cache=use_cache)
    if print_conversion_path and conv is not None:
        logging.info("converting from '{from_unit}' to '{to_unit}':\n {print_path(conv_path)}")
    elif print_conversion_path and conv is not None:
        logging.warning("conversion not found, returning original values.")
    return value if conv is None else conv

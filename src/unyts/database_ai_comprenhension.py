#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 23:15:37 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>

OPTIMIZED VERSION - Using comprehensions and helper functions for faster network building
"""

__version__ = '0.6.4'
__release__ = 20250601
__all__ = ['units_network', 'network_to_frame', 'save_memory', 'load_memory', 'clean_memory', 'delete_cache', 'set_fvf']


import os

from .dictionaries import SI, SI_butK, SI_order, OGF, OGF_order, DATA, DATA_order, dictionary
from .units.def_conversions import *
from .network import UDigraph, UNode, Conversion
from .parameters import unyts_parameters_
from .helpers.logger import logger
from os.path import isfile
from json import dump as json_dump

try:
    from cloudpickle import dump as cloudpickle_dump, load as cloudpickle_load
    _cloudpickle_ = True
except ModuleNotFoundError:
    if unyts_parameters_.cache_:
        logger.warning("Missing `cloudpickle` package. Not able to cache network dictionary.")
    _cloudpickle_ = False


def save_memory(path=None) -> None:
    units_network.save_memory(path)


def load_memory(path=None) -> None:
    units_network.load_memory(path)


def clean_memory(path=None) -> None:
    units_network.clean_memory()


def delete_cache() -> None:
    for each in ('search_memory.cache', 'units_network.cache', 'units_dictionary.cache',
                 'temperature_ratio_conversions.cache', 'unitless_names.cache'):
        path = unyts_parameters_.get_user_folder() + each
        if os.path.exists(path):
            os.remove(path)


def set_fvf(fvf=None) -> None:
    def valid_fvf(fvf):
        if type(fvf) is str:
            try:
                fvf = float(fvf)
            except ValueError:
                return False
        if type(fvf) in (int, float):
            if fvf <= 0:
                return False
            else:
                return fvf
        else:
            return False
    if fvf is None:
        print('Please enter formation Volume factor (FVF) in reservoir_volume/standard_volume:')
        while fvf is None:
            fvf = input(' FVF (rV/stV) = ')
            if not valid_fvf(fvf):
                fvf = None
            else:
                fvf = valid_fvf(fvf)
    units_network.set_fvf(fvf)
    unyts_parameters_.fvf_ = fvf
    logger.info(f"FVF set to {fvf} rV/stV")


def get_fvf() -> str:
    if units_network.fvf is not None:
        return str(round(units_network.fvf, 4))
    elif unyts_parameters_.fvf:
        set_fvf(unyts_parameters_.fvf)
    else:
        return ""


# ============================================================================
# HELPER FUNCTIONS FOR PROCESSING UNIT KINDS
# ============================================================================

def _process_basic_units(network, unit_kind, unit_names):
    """Add basic unit nodes without special processing"""
    for unit_name in unit_names:
        network.add_node(UNode(unit_name))


def _process_names(network, unit_kind, unit_data):
    """Process _NAMES unit kinds - creates aliases"""
    base_kind = unit_kind.split('_')[0]
    for unit_name in unit_data:
        network.add_node(UNode(unit_name))
        dictionary[base_kind].append(unit_name)
        for second_name in unit_data[unit_name]:
            network.add_node(UNode(second_name))
            network.add_edge(Conversion(network.get_node(second_name), network.get_node(unit_name), equality, alias=True))
            network.add_edge(Conversion(network.get_node(unit_name), network.get_node(second_name), equality, alias=True))
            dictionary[base_kind].append(second_name)


def _process_spaces(network, unit_kind, unit_data):
    """Process _SPACES unit kinds - creates variants with dashes and underscores"""
    base_kind = unit_kind.split('_')[0]
    is_dict = isinstance(unit_data, dict)
    
    for rep in ['-', '_']:
        for unit_name in unit_data:
            if ' ' in unit_name:
                network.add_node(UNode(unit_name))
                replaced = unit_name.replace(' ', rep)
                network.add_node(UNode(replaced))
                dictionary[base_kind].extend([unit_name, replaced])
                network.add_edge(Conversion(network.get_node(unit_name), network.get_node(replaced), equality))
                network.add_edge(Conversion(network.get_node(replaced), network.get_node(unit_name), equality))
                
                if is_dict:
                    for second_name in unit_data[unit_name]:
                        if ' ' in second_name:
                            network.add_node(UNode(second_name))
                            replaced_second = second_name.replace(' ', rep)
                            network.add_node(UNode(replaced_second))
                            network.add_edge(Conversion(network.get_node(replaced_second), network.get_node(second_name), equality))
                            network.add_edge(Conversion(network.get_node(second_name), network.get_node(replaced_second), equality))
                            dictionary[base_kind].extend([second_name, replaced_second])
            else:
                if is_dict:
                    for second_name in unit_data[unit_name]:
                        if ' ' in second_name:
                            network.add_node(UNode(second_name))
                            replaced_second = second_name.replace(' ', rep)
                            network.add_node(UNode(replaced_second))
                            network.add_edge(Conversion(network.get_node(replaced_second), network.get_node(second_name), equality))
                            network.add_edge(Conversion(network.get_node(second_name), network.get_node(replaced_second), equality))
                            dictionary[base_kind].extend([second_name, replaced_second])


def _process_si_prefixes(network, unit_kind, unit_names, prefix_dict, order_index):
    """Process SI prefix combinations"""
    base_kind = unit_kind.split('_')[0]
    for unit_name in unit_names:
        network.add_node(UNode(unit_name))
        dictionary[base_kind].append(unit_name)
        for prefix, conversions in prefix_dict.items():
            prefixed = prefix + unit_name
            network.add_node(UNode(prefixed))
            network.add_edge(Conversion(network.get_node(prefixed), network.get_node(unit_name), conversions[order_index]))
            network.add_edge(Conversion(network.get_node(unit_name), network.get_node(prefixed), conversions[order_index], reverse=True))
            dictionary[base_kind].append(prefixed)


def _process_plural(network, unit_kind, unit_data):
    """Process _PLURALwS - adds plural forms"""
    base_kind = unit_kind.split('_')[0]
    is_dict = isinstance(unit_data, dict)
    
    unit_list = list(unit_data.keys()) if is_dict else list(unit_data)
    for unit_name in unit_list:
        network.add_node(UNode(unit_name))
        plural = unit_name + 's'
        network.add_node(UNode(plural))
        network.add_edge(Conversion(network.get_node(unit_name), network.get_node(plural), equality))
        network.add_edge(Conversion(network.get_node(plural), network.get_node(unit_name), equality))
        dictionary[base_kind].append(plural)


def _process_case(network, unit_kind, unit_data, case_func):
    """Process _UPPER or _LOWER - adds case variants"""
    base_kind = unit_kind.split('_')[0]
    is_dict = isinstance(unit_data, dict)
    
    for unit_name in unit_data:
        network.add_node(UNode(unit_name))
        cased = case_func(unit_name)
        network.add_node(UNode(cased))
        network.add_edge(Conversion(network.get_node(unit_name), network.get_node(cased), equality))
        network.add_edge(Conversion(network.get_node(cased), network.get_node(unit_name), equality))
        dictionary[base_kind].append(cased)
        
        if is_dict:
            for second_name in unit_data[unit_name]:
                network.add_node(UNode(second_name))
                cased_second = case_func(second_name)
                network.add_node(UNode(cased_second))
                network.add_edge(Conversion(network.get_node(second_name), network.get_node(cased_second), equality))
                network.add_edge(Conversion(network.get_node(cased_second), network.get_node(second_name), equality))
                dictionary[base_kind].append(cased_second)


def _add_fixed_conversions(network):
    """Add all the fixed conversion relationships"""
    conversions = [
        # Percentage & fraction
        ('fraction', 'percentage', fraction__to__percentage),
        ('percentage', 'fraction', percentage__to__fraction),
        
        # Time conversions
        ('second', 'millisecond', second__to__millisecond),
        ('minute', 'second', minute__to__second),
        ('hour', 'minute', hour__to__minute),
        ('day', 'hour', day__to__hour),
        ('day', 'month', day__to__month),
        ('week', 'day', week__to__day),
        ('year', 'month', year__to__month),
        ('year', 'day', year__to__day),
        ('lustrum', 'year', lustrum__to__year),
        ('decade', 'year', decade__to__year),
        ('century', 'year', century__to__year),
        
        # Temperature conversions
        ('Celsius', 'Kelvin', Celsius__to__Kelvin),
        ('Kelvin', 'Celsius', Kelvin__to__Celsius),
        ('Celsius', 'Fahrenheit', Celsius__to__Fahrenheit),
        ('Fahrenheit', 'Celsius', Fahrenheit__to__Celsius),
        ('Fahrenheit', 'Rankine', Fahrenheit__to__Rankine),
        ('Rankine', 'Fahrenheit', Rankine__to__Fahrenheit),
        ('Rankine', 'Kelvin', Rankine__to__Kelvin),
        ('Kelvin', 'Rankine', Kelvin__to__Rankine),
        
        # Length conversions
        ('yard', 'meter', yard__to__meter),
        ('inch', 'thou', inch__to__thou),
        ('inch', 'tenth', inch__to__tenth),
        ('foot', 'inch', foot__to__inch),
        ('yard', 'foot', yard__to__foot),
        ('chain', 'yard', chain__to__yard),
        ('furlong', 'chain', furlong__to__chain),
        ('mile', 'furlong', mile__to__furlong),
        ('league', 'mile', league__to__mile),
        ('nautical league', 'nautical mile', nautical_league__to__nautical_mile),
        ('nautical mile', 'meter', nautical_mile__to__meter),
        ('rod', 'yard', rod__to__yard),
        ('astronomical unit', 'meter', astronomical_unit__to__meter),
        ('parsec', 'astronomical unit', parsec__to__astronomical_unit),
        ('light year', 'meter', light_year__to__meter),
        ('scandinavian mile', 'kilometer', scandinavian_mile__to__kilometer),
        
        # Velocity conversion
        ('mile per hour', 'kilometer per hour', mile_per_hour__to__kilometer_per_hour),
        
        # Area conversions
        ('square kilometer', 'square meter', square_kilometer__to__square_meter),
        ('square mile', 'acre', square_mile__to__acre),
        ('acre', 'square yard', acre__to__square_yard),
        ('square rod', 'square yard', square_rod__to__square_yard),
        ('square yard', 'square foot', square_yard__to__square_foot),
        ('square foot', 'square inch', square_foot__to__square_inch),
        ('square foot', 'square meter', square_foot__to__square_meter),
        ('square inch', 'square thou', square_inch__to__square_thou),
        ('square inch', 'square tenth', square_inch__to__square_tenth),
        ('square chain', 'square yard', square_chain__to__square_yard),
        ('square furlong', 'square chain', square_furlong__to__square_chain),
        ('square mile', 'square furlong', square_mile__to__square_furlong),
        ('square league', 'square mile', square_league__to__square_mile),
        ('Darcy', 'µm2', Darcy__to__µm2),
        
        # Volume conversions
        ('litre', 'cubic centimeter', litre__to__cubic_centimeter),
        ('gill', 'fluid ounce', gill__to__fluid_ounce),
        ('pint', 'gill', pint__to__gill),
        ('quart', 'pint', quart__to__pint),
        ('gallonUS', 'fluid ounce', gallonUS__to__fluid_ounce),
        ('gallonUS', 'quart', gallonUS__to__quart),
        ('gallonUS', 'cubic inch', gallonUS__to__cubic_inch),
        ('gallonUK', 'quartUK', gallonUK__to__quartUK),
        ('gallonUK', 'fluid ounce UK', gallonUK__to__fluid_ounce_UK),
        ('gallonUK', 'litre', gallonUK__to__litre),
        ('gillUK', 'fluid ounce UK', gillUK__to__fluid_ounce_UK),
        ('pintUK', 'gillUK', pintUK__to__gillUK),
        ('quartUK', 'pintUK', quartUK__to__pintUK),
        ('gallonUK', 'liter', gallonUK__to__liter),
        ('cubic foot', 'cubic meter', cubic_foot__to__cubic_meter),
        ('standard cubic foot', 'standard cubic meter', standard_cubic_foot__to__standard_cubic_meter),
        ('standard barrel', 'USgal', standard_barrel__to__USgal),
        ('standard cubic meter', 'standard barrel', standard_cubic_meter__to__standard_barrel),
        ('standard barrel', 'standard cubic foot', standard_barrel__to__standard_cubic_foot),
        ('reservoir cubic meter', 'reservoir barrel', reservoir_cubic_meter__to__reservoir_barrel),
        ('reservoir cubic meter', 'standard cubic meter', reservoir_cubic_meter__to__standard_cubic_meter),
        ('cubic inch', 'cubic thou', cubic_inch__to__cubic_thou),
        ('cubic inch', 'cubic tenth', cubic_inch__to__cubic_tenth),
        ('cubic foot', 'cubic inch', cubic_foot__to__cubic_inch),
        ('cubic yard', 'cubic foot', cubic_yard__to__cubic_foot),
        ('cubic chain', 'cubic yard', cubic_chain__to__cubic_yard),
        ('cubic furlong', 'cubic chain', cubic_furlong__to__cubic_chain),
        ('cubic mile', 'cubic furlong', cubic_mile__to__cubic_furlong),
        ('cubic league', 'cubic mile', cubic_league__to__cubic_mile),
        
        # Pressure conversions
        ('psi gauge', 'absolute psi', psi_gauge__to__absolute_psi),
        ('absolute psi', 'psi gauge', absolute_psi__to__psi_gauge),
        ('bar gauge', 'absolute bar', bar_gauge__to__absolute_bar),
        ('absolute bar', 'bar gauge', absolute_bar__to__bar_gauge),
        ('absolute bar', 'absolute psi', absolute_bar__to__absolute_psi),
        ('bar gauge', 'psi gauge', bar_gauge__to__psi_gauge),
        ('bar', 'psi', bar__to__psi),
        ('psi', 'bar', psi__to__bar),
        ('absolute bar', 'Pascal', absolute_bar__to__Pascal),
        ('atmosphere', 'Pascal', atmosphere__to__Pascal),
        ('atmosphere', 'Torr', atmosphere__to__Torr),
        ('absolute bar', 'bar', equality),
        ('absolute psi', 'psi', equality),
        ('bar gauge', 'bar', equality),
        ('psi gauge', 'psi', equality),
        ('absolute bar', 'kilogram/square centimeter', absolute_bar__to__kilogram_slash_square_centimeter),
        
        # Mass conversion
        ('grain', 'milligrams', grain__to__milligrams),
        ('pennyweight', 'grain', pennyweight__to__grain),
        ('dram', 'pound', dram__to__pound),
        ('stone', 'pound', stone__to__pound),
        ('quarter', 'stone', quarter__to__stone),
        ('weight ounce', 'dram', weight_ounce__to__dram),
        ('pound', 'weight ounce', pound__to__weight_ounce),
        ('long hundredweight', 'quarter', long_hundredweight__to__quarter),
        ('short hundredweight', 'pound', short_hundredweight__to__pound),
        ('short ton', 'short hundredweight', short_ton__to__short_hundredweight),
        ('long ton', 'long hundredweight', long_ton__to__long_hundredweight),
        ('metric ton', 'kilogram', metric_ton__to__kilogram),
        ('kilogram', 'gram', kilogram__to__gram),
        ('pound', 'kilogram', pound__to__kilogram),
        
        # Force conversion
        ('kilogram mass', 'kilogram force', kilogram_mass__to__kilogram_force),
        ('kilogram force', 'kilogram mass', kilogram_force__to__kilogram_mass),
        ('Dyne', 'Newton', Dyne__to__Newton),
        ('Newton', 'Dyne', Newton__to__Dyne),
        ('pound force', 'kilogram force', pound__to__kilogram),
        ('kilogram force', 'Newton', kilogram_force__to__Newton),
        
        # Energy Conversion
        ('Joule', 'gram calorie', Joule__to__gram_calorie),
        ('Kilojoule', 'Joule', Kilojoule__to__Joule),
        ('Kilojoule', 'kilowatt hour', Kilojoule__to__kilowatt_hour),
        ('Kilojoule', 'British thermal unit', Kilojoule__to__British_thermal_unit),
        
        # Power conversion
        ('Horsepower', 'Watt', Horsepower__to__Watt),
        
        # Density conversion
        ('API', 'SgO', API__to__SgO),
        ('SgO', 'API', SgO__to__API),
        ('API', 'g/cc', API__to__g_slash_cc),
        ('g/cc', 'API', g_slash_cc__to__API),
        ('SgO', 'g/cc', equality),
        ('SgW', 'g/cc', equality),
        ('SgG', 'kg/m3', SgG__to__kg_slash_m3),
        ('psia/ft', 'lb/ft3', psia_slash_ft__to__lb_slash_ft3),
        ('psi/ft', 'lb/ft3', psi_slash_ft__to__lb_slash_ft3),
        ('psig/ft', 'lb/ft3', psig_slash_ft__to__lb_slash_ft3),
        ('bara/m', 'kg/m3', bara_slash_m__to__kg_slash_m3),
        ('bar/m', 'kg/m3', bar_slash_m__to__kg_slash_m3),
        ('barg/m', 'kg/m3', barg_slash_m__to__kg_slash_m3),
        ('g/cm3', 'lb/ft3', g_slash_cm3__to__lb_slash_ft3),
        ('lb/ft3', 'lb/stb', lb_slash_ft3__to__lb_slash_stb),
        
        # Viscosity conversions
        ('Pascal*second', 'Poise', Pascal_star_second__to__Poise),
        ('Pascal*second', 'Reyn', Pascal_star_second__to__Reyn),
        ('Pascal*second', 'Poiseuille', equality),
        
        # Data conversions
        ('byte', 'bit', byte__to__bit),
    ]
    
    for source, target, conversion in conversions:
        network.add_edge(Conversion(network.get_node(source), network.get_node(target), conversion))


def _load_network():
    logger.info('preparing units network...')
    network = UDigraph()

    # Process each unit kind
    for unit_kind, unit_data in dictionary.items():
        if '_' not in unit_kind:
            # Basic units without special processing
            _process_basic_units(network, unit_kind, unit_data)
            continue
        
        # Process special unit kinds
        base_kind = unit_kind.split('_')[0]
        
        if '_NAMES' in unit_kind:
            _process_names(network, unit_kind, unit_data)
        
        if '_SPACES' in unit_kind:
            _process_spaces(network, unit_kind, unit_data)
        
        # SI prefix processing
        if '_SI' in unit_kind:
            if '_linearSI' in unit_kind and base_kind in SI_order[2]:
                _process_si_prefixes(network, unit_kind, unit_data, SI, 0)
            elif '_KnotSI' in unit_kind:
                if base_kind in SI_order[0]:
                    _process_si_prefixes(network, unit_kind, unit_data, SI_butK, 0)
                elif base_kind in SI_order[1]:
                    _process_si_prefixes(network, unit_kind, unit_data, SI_butK, 1)
                elif base_kind in SI_order[2]:
                    _process_si_prefixes(network, unit_kind, unit_data, SI_butK, 2)
            else:
                if base_kind in SI_order[0]:
                    _process_si_prefixes(network, unit_kind, unit_data, SI, 0)
                elif base_kind in SI_order[1]:
                    _process_si_prefixes(network, unit_kind, unit_data, SI, 1)
                elif base_kind in SI_order[2]:
                    _process_si_prefixes(network, unit_kind, unit_data, SI, 2)
        
        # DATA prefix processing
        if '_DATA' in unit_kind:
            if base_kind in DATA_order[0]:
                _process_si_prefixes(network, unit_kind, unit_data, DATA, 0)
            elif base_kind in DATA_order[1]:
                _process_si_prefixes(network, unit_kind, unit_data, DATA, 1)
        
        # OGF prefix processing
        if '_OGF' in unit_kind and base_kind in OGF_order[2]:
            _process_si_prefixes(network, unit_kind, unit_data, OGF, 2)
        
        # Plural processing
        if '_PLURALwS' in unit_kind:
            _process_plural(network, unit_kind, unit_data)
            
            if '_UPPER' in unit_kind:
                for unit_name in (list(unit_data.keys()) if isinstance(unit_data, dict) else list(unit_data)):
                    network.add_node(UNode(unit_name))
                    upper_plural = unit_name.upper() + 'S'
                    network.add_node(UNode(upper_plural))
                    network.add_edge(Conversion(network.get_node(unit_name), network.get_node(upper_plural), equality))
                    network.add_edge(Conversion(network.get_node(upper_plural), network.get_node(unit_name), equality))
                    dictionary[base_kind].append(upper_plural)
            
            if '_LOWER' in unit_kind:
                for unit_name in (list(unit_data.keys()) if isinstance(unit_data, dict) else list(unit_data)):
                    network.add_node(UNode(unit_name))
                    lower_plural = unit_name.lower() + 's'
                    network.add_node(UNode(lower_plural))
                    network.add_edge(Conversion(network.get_node(unit_name), network.get_node(lower_plural), equality))
                    network.add_edge(Conversion(network.get_node(lower_plural), network.get_node(unit_name), equality))
                    dictionary[base_kind].append(lower_plural)
        
        # Case processing (without plural)
        if '_UPPER' in unit_kind and '_PLURALwS' not in unit_kind:
            _process_case(network, unit_kind, unit_data, str.upper)
        
        if '_LOWER' in unit_kind and '_PLURALwS' not in unit_kind:
            _process_case(network, unit_kind, unit_data, str.lower)

    # Add all fixed conversions
    _add_fixed_conversions(network)

    # Process REVERSE relationships
    for unit_kind in list(dictionary.keys()):
        if '_REVERSE' in unit_kind:
            unit_list = list(dictionary[unit_kind].keys()) if isinstance(dictionary[unit_kind], dict) else list(dictionary[unit_kind])
            for unit_name in unit_list:
                unit_node = network.get_node(unit_name)
                for other_node in network.children_of(unit_node):
                    if unit_node != other_node:
                        idx = network.edges[unit_node][0].index(other_node)
                        network.add_edge(Conversion(other_node, unit_node, network.edges[unit_node][1][idx], True))

    # Process FROMvolume relationships
    for unit_kind in list(dictionary.keys()):
        if '_FROMvolume' in unit_kind:
            base_kind = unit_kind.split('_')[0]
            if base_kind in SI_order[2]:
                for unit_name in list(dictionary[unit_kind]):
                    network.add_node(UNode(unit_name))
                    dictionary[base_kind].append(unit_name)
                    base_unit = unit_name.split('/')[0]
                    time_unit = unit_name.split('/')[1]
                    
                    for other_node in network.children_of(network.get_node(base_unit)):
                        if network.get_node(base_unit) != other_node:
                            logger.warning('R   3: ' + unit_name, other_node.get_name())
                            other_rate = other_node.get_name() + '/' + time_unit
                            network.add_node(UNode(other_rate))
                            
                            time_node = network.get_node(time_unit)
                            idx = network.edges[time_node][0].index(other_node)
                            conversion = network.edges[time_node][1][idx]
                            
                            network.add_edge(Conversion(network.get_node(unit_name), network.get_node(other_rate), conversion))
                            network.add_edge(Conversion(network.get_node(other_rate), network.get_node(unit_name), conversion, True))

    # Clean up dictionary - remove temporary keys and deduplicate
    to_remove = [k for k in dictionary.keys() if '_' in k]
    for key in to_remove:
        dictionary.pop(key)
    
    for key in dictionary:
        if key != 'UserUnits':
            dictionary[key] = tuple(set(dictionary[key]))
    
    # Merge data dictionaries
    dictionary['Data'] = tuple(dictionary['dataBYTE'] + dictionary['dataBIT'])
    del dictionary['dataBYTE']
    del dictionary['dataBIT']
    dictionary['UserUnits'] = list(dictionary['UserUnits'])
    
    return network


def _create_Rates() -> None:
    rates = list(dictionary['Rate']) if 'Rate' in dictionary else []
    rates += [f"{v}/{t}" for v in dictionary['Volume'] for t in dictionary['Time']]
    rates += [f"{w}/{t}" for w in dictionary['Weight'] for t in dictionary['Time']]
    rates += [f"{d}/{t}" for d in dictionary['Data'] for t in dictionary['Time']]
    dictionary['Rate'] = tuple(set(rates))


def _create_VolumeRatio() -> None:
    ratio = list(dictionary['VolumeRatio']) if 'VolumeRatio' in dictionary else []
    ratio += [f"{num}/{den}" for num in dictionary['Volume'] for den in dictionary['Volume']]
    dictionary['VolumeRatio'] = tuple(set(ratio))


def _create_Density() -> None:
    density = list(dictionary['Density']) if 'Density' in dictionary else []
    density += [f"{m}/{v}" for m in dictionary['Mass'] for v in dictionary['Volume']]
    dictionary['Density'] = tuple(set(density))


def _create_Velocity() -> None:
    velocity = list(dictionary['Velocity']) if 'Velocity' in dictionary else []
    velocity += [f"{l}/{t}" for l in dictionary['Length'] for t in dictionary['Time']]
    dictionary['Velocity'] = tuple(set(velocity))


def _create_Power() -> None:
    power = list(dictionary['Power']) if 'Power' in dictionary else []
    power += [f"{e}/{t}" for e in dictionary['Energy'] for t in dictionary['Time']]
    power += [f"{v}*{c}" for v in dictionary['Voltage'] for c in dictionary['Current']]
    power += [f"{c}*{v}" for v in dictionary['Voltage'] for c in dictionary['Current']]
    power += [f"{c}2*{r}" for r in dictionary['Resistance'] for c in dictionary['Current']]
    power += [f"{r}*{c}2" for r in dictionary['Resistance'] for c in dictionary['Current']]
    dictionary['Power'] = tuple(set(power))


def _create_Frequency() -> None:
    frequency = list(dictionary['Frequency']) if 'Frequency' in dictionary else []
    frequency += [f"1/{t}" for t in dictionary['Time']]
    dictionary['Frequency'] = tuple(set(frequency))


def _create_Conductance() -> None:
    conductance = list(dictionary['Conductance']) if 'Conductance' in dictionary else []
    conductance += [f"1/{r}" for r in dictionary['Resistance']]
    dictionary['Conductance'] = tuple(set(conductance))


def _create_Capacitance_Charge() -> None:
    capacitance = list(dictionary['Capacitance']) if 'Capacitance' in dictionary else []
    charge = list(dictionary['Charge']) if 'Charge' in dictionary else []
    
    capacitance += [f"{ch}/{v}" for v in dictionary['Voltage'] for ch in dictionary['Charge']]
    charge += [f"{cap}*{v}" for v in dictionary['Voltage'] for cap in dictionary['Capacitance']]
    charge += [f"{v}*{cap}" for v in dictionary['Voltage'] for cap in dictionary['Capacitance']]
    
    dictionary['Capacitance'] = tuple(set(capacitance))
    dictionary['Charge'] = tuple(set(charge))


def _create_Voltage_Current_Resistance() -> None:
    voltage = list(dictionary['Voltage']) if 'Voltage' in dictionary else []
    current = list(dictionary['Current']) if 'Current' in dictionary else []
    resistance = list(dictionary['Resistance']) if 'Resistance' in dictionary else []
    
    voltage += [f"{c}*{r}" for r in dictionary['Resistance'] for c in dictionary['Current']]
    voltage += [f"{r}*{c}" for r in dictionary['Resistance'] for c in dictionary['Current']]
    voltage += [f"{p}/{c}" for p in dictionary['Power'] for c in dictionary['Current']]
    
    current += [f"{v}/{r}" for r in dictionary['Resistance'] for v in dictionary['Voltage']]
    current += [f"{p}/{v}" for p in dictionary['Power'] for v in dictionary['Voltage']]
    
    resistance += [f"{v}/{c}" for c in dictionary['Current'] for v in dictionary['Voltage']]
    
    dictionary['Voltage'] = tuple(set(voltage))
    dictionary['Current'] = tuple(set(current))
    dictionary['Resistance'] = tuple(set(resistance))


def _create_Pressure() -> None:
    pressure = list(dictionary['Pressure']) if 'Pressure' in dictionary else []
    pressure += [f"{w}/{a}" for w in dictionary['Weight'] for a in dictionary['Area']]
    dictionary['Pressure'] = tuple(set(pressure))


def _create_ProductivityIndex() -> None:
    pi = list(dictionary['ProductivityIndex']) if 'ProductivityIndex' in dictionary else []
    pi += [f"{v}/{t}/{p}" for v in dictionary['Volume'] for t in dictionary['Time'] for p in dictionary['Pressure']]
    dictionary['ProductivityIndex'] = tuple(set(pi))


def _create_PressureGradient() -> None:
    pg = list(dictionary['PressureGradient']) if 'PressureGradient' in dictionary else []
    pg += [f"{p}/{l}" for p in dictionary['Pressure'] for l in dictionary['Length']]
    dictionary['PressureGradient'] = tuple(set(pg))


def _create_TemperatureGradient() -> None:
    tg = list(dictionary['TemperatureGradient']) if 'TemperatureGradient' in dictionary else []
    tg += [f"{t}/{l}" for t in dictionary['Temperature'] for l in dictionary['Length']]
    dictionary['TemperatureGradient'] = tuple(set(tg))


def _create_Acceleration() -> None:
    acceleration = list(dictionary['Acceleration']) if 'Acceleration' in dictionary else []
    acceleration += [
        f"{l}/{t1}2" if t1 == t2 else f"{l}/{t1}/{t2}"
        for l in dictionary['Length']
        for t1 in dictionary['Time']
        for t2 in dictionary['Time']
    ]
    dictionary['Acceleration'] = tuple(set(acceleration))


def _complete_products() -> None:
    for key in dictionary:
        products = [u for u in dictionary[key] if '/' not in u and len(u.split('*')) == 2]
        reversed_products = [f"{u.split('*')[1]}*{u.split('*')[0]}" for u in products]
        dictionary[key] = tuple(set(list(dictionary[key]) + reversed_products))


def _rebuild_units():
    logger.warning('Rebuilding units dictionary...')
    from .dictionaries import _load_dictionary
    dictionary, temperatureRatioConversions, unitless_names = _load_dictionary()
    units_network = _load_network()
    _clean_network()
    unyts_parameters_.reload_ = True
    unyts_parameters_.save_params()
    return units_network, dictionary, temperatureRatioConversions, unitless_names


def network_to_frame():
    try:
        from pandas import DataFrame
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Required package `pandas` not found.\nTo install Pandas: `pip install pandas`")

    frame = DataFrame(data={}, columns=['source', 'target', 'lambda'])
    i = 0
    for node in units_network.edges:
        for children in units_network.children_of(node):
            frame.loc[i, ['source', 'target', 'lambda']] = [node.get_name(), children.get_name(),
                                                            units_network.conversion(node, children)]
            i += 1
    return frame.drop_duplicates(['source', 'target'])


def _clean_network():
    units_network.edges = {k: v for k, v in units_network.edges.items() if v != ([],[])}


# Load the network into an instance of the graph database
if not unyts_parameters_.reload_ and \
        isfile(unyts_parameters_.get_user_folder() + 'units_network.cache') and \
        (not _cloudpickle_ or (_cloudpickle_ and isfile(unyts_parameters_.get_user_folder() + 'units_dictionary.cache'))) and \
        isfile(unyts_parameters_.get_user_folder() + 'temperature_ratio_conversions.cache') and \
        isfile(unyts_parameters_.get_user_folder() + 'unitless_names.cache'):
    try:
        with open(unyts_parameters_.get_user_folder() + 'units_network.cache', 'rb') as f:
            units_network = cloudpickle_load(f)
        logger.info('units network loaded from cache...')
        unyts_parameters_.reload_ = False
        unyts_parameters_.save_params()
    except:
        logger.error("Failed to load from cache. Creating new dictionaries and saving them to cache...")
        units_network, dictionary, temperatureRatioConversions, unitless_names = _rebuild_units()
else:
    units_network = _load_network()
    # Load the dictionary with ratio units
    _create_Rates()
    _create_VolumeRatio()
    _create_Density()
    _create_Velocity()
    _create_Acceleration()
    _create_ProductivityIndex()
    _create_PressureGradient()
    _create_Pressure()
    _create_TemperatureGradient()
    _create_Power()
    _create_Frequency()
    _create_Conductance()
    _create_Capacitance_Charge()
    _create_Voltage_Current_Resistance()
    _complete_products()
    # Clean empty edges
    _clean_network()

    unyts_parameters_.reload_ = False
    unyts_parameters_.save_params()
    if unyts_parameters_.cache_:
        logger.info('saving units network and dictionary to cache...')
        if _cloudpickle_:
            with open(unyts_parameters_.get_user_folder() + 'units_network.cache', 'wb') as f:
                cloudpickle_dump(units_network, f)
        with open(unyts_parameters_.get_user_folder() + 'units_dictionary.cache', 'w') as f:
            json_dump(dictionary, f)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 23:15:37 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>
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


def _load_network():
    logger.info('preparing units network...')
    network = UDigraph()

    for unit_kind in dictionary:
        if '_' not in unit_kind:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
        if '_NAMES' in unit_kind:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for secondName in dictionary[unit_kind][unit_name]:
                    network.add_node(UNode(secondName))
                    network.add_edge(Conversion(network.get_node(secondName), network.get_node(unit_name), equality, alias=True))
                    network.add_edge(Conversion(network.get_node(unit_name), network.get_node(secondName), equality, alias=True))
                    dictionary[unit_kind.split('_')[0]].append(secondName)
        if '_SPACES' in unit_kind:
            for rep in ['-', '_']:
                for unit_name in dictionary[unit_kind]:
                    if ' ' in unit_name:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.replace(' ', rep)))
                        dictionary[unit_kind.split('_')[0]].append(unit_name)
                        dictionary[unit_kind.split('_')[0]].append(unit_name.replace(' ', rep))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.replace(' ', rep)),
                                       equality))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.replace(' ', rep)),
                                       equality))
                        if type(dictionary[unit_kind]) is dict:
                            for secondName in dictionary[unit_kind][unit_name]:
                                if ' ' in secondName:
                                    network.add_node(UNode(secondName))
                                    network.add_node(UNode(secondName.replace(' ', rep)))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName.replace(' ', rep)), network.get_node(secondName),
                                                   equality))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName), network.get_node(secondName.replace(' ', rep)),
                                                   equality))
                                    dictionary[unit_kind.split('_')[0]].append(secondName)
                                    dictionary[unit_kind.split('_')[0]].append(secondName.replace(' ', rep))
                    else:
                        if type(dictionary[unit_kind]) is dict:
                            for secondName in dictionary[unit_kind][unit_name]:
                                if ' ' in secondName:
                                    network.add_node(UNode(secondName))
                                    network.add_node(UNode(secondName.replace(' ', rep)))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName.replace(' ', rep)), network.get_node(secondName),
                                                   equality))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName), network.get_node(secondName.replace(' ', rep)),
                                                   equality))
                                    dictionary[unit_kind.split('_')[0]].append(secondName)
                                    dictionary[unit_kind.split('_')[0]].append(secondName.replace(' ', rep))

        if '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[0]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][0]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][0],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        elif '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[1]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][1]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][1],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        elif '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][2]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][2],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        elif '_linearSI' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][0]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][0],
                                   reverse=True))
        elif '_KnotSI' in unit_kind and unit_kind.split('_')[0] in SI_order[0]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI_butK:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name),
                                   SI_butK[prefix][0]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name),
                                   SI_butK[prefix][0],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        elif '_KnotSI' in unit_kind and unit_kind.split('_')[0] in SI_order[1]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI_butK:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name),
                                   SI_butK[prefix][1]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name),
                                   SI_butK[prefix][1],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        elif '_KnotSI' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI_butK:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name),
                                   SI_butK[prefix][2]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name),
                                   SI_butK[prefix][2],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_DATA' in unit_kind and unit_kind.split('_')[0] in DATA_order[0]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in DATA:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), DATA[prefix][0]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), DATA[prefix][0],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_DATA' in unit_kind and unit_kind.split('_')[0] in DATA_order[1]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in DATA:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), DATA[prefix][1]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), DATA[prefix][1],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_OGF' in unit_kind and unit_kind.split('_')[0] in OGF_order[2]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in OGF:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), OGF[prefix][2]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), OGF[prefix][2],
                                   reverse=True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_PLURALwS' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name + 's'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name + 's'), equality))
                    network.add_edge(
                        Conversion(network.get_node(unit_name + 's'), network.get_node(unit_name), equality))
                    dictionary[unit_kind.split('_')[0]].append(unit_name + 's')
            else:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name + 's'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name + 's'), equality))
                    network.add_edge(
                        Conversion(network.get_node(unit_name + 's'), network.get_node(unit_name), equality))
                    dictionary[unit_kind.split('_')[0]].append(unit_name + 's')
            if '_UPPER' in unit_kind:
                if type(dictionary[unit_kind]) is dict:
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.upper() + 'S'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.upper() + 'S'),
                                       equality))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.upper() + 'S'), network.get_node(unit_name),
                                       equality))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.upper() + 'S')
                else:
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.upper() + 'S'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.upper() + 'S'),
                                       equality))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.upper() + 'S'), network.get_node(unit_name),
                                       equality))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.upper() + 'S')
            if '_LOWER' in unit_kind:
                if type(dictionary[unit_kind]) is dict:
                    # list_names = list(dictionary[unit_kind].keys())
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.lower() + 's'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.lower() + 's'),
                                       equality))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.lower() + 's'), network.get_node(unit_name),
                                       equality))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.lower() + 's')
                else:
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.lower() + 's'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.lower() + 's'),
                                       equality))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.lower() + 's'), network.get_node(unit_name),
                                       equality))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.lower() + 's')
        if '_UPPER' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.upper()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.upper()), equality))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.upper()), network.get_node(unit_name), equality))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.upper())
                    for secondName in dictionary[unit_kind][unit_name]:
                        network.add_node(UNode(secondName))
                        network.add_node(UNode(secondName.upper()))
                        network.add_edge(
                            Conversion(network.get_node(secondName), network.get_node(secondName.upper()), equality))
                        network.add_edge(
                            Conversion(network.get_node(secondName.upper()), network.get_node(secondName), equality))
                        dictionary[unit_kind.split('_')[0]].append(secondName.upper())
            else:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.upper()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.upper()), equality))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.upper()), network.get_node(unit_name), equality))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.upper())
        if '_LOWER' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.lower()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.lower()), equality))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.lower()), network.get_node(unit_name), equality))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.lower())
                    for secondName in dictionary[unit_kind][unit_name]:
                        network.add_node(UNode(secondName))
                        network.add_node(UNode(secondName.lower()))
                        network.add_edge(
                            Conversion(network.get_node(secondName), network.get_node(secondName.lower()), equality))
                        network.add_edge(
                            Conversion(network.get_node(secondName.lower()), network.get_node(secondName), equality))
                        dictionary[unit_kind.split('_')[0]].append(secondName.lower())
            else:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.lower()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.lower()), equality))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.lower()), network.get_node(unit_name), equality))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.lower())
        if '_INVERSE' in unit_kind:
            pass

    # Percentage & fraction :
    network.add_edge(Conversion(network.get_node('fraction'), network.get_node('percentage'), fraction__to__percentage))
    network.add_edge(Conversion(network.get_node('percentage'), network.get_node('fraction'), percentage__to__fraction))

    # Time conversions
    network.add_edge(Conversion(network.get_node('second'), network.get_node('millisecond'), second__to__millisecond))
    network.add_edge(Conversion(network.get_node('minute'), network.get_node('second'), minute__to__second))
    network.add_edge(Conversion(network.get_node('hour'), network.get_node('minute'), hour__to__minute))
    network.add_edge(Conversion(network.get_node('day'), network.get_node('hour'), day__to__hour))
    network.add_edge(Conversion(network.get_node('day'), network.get_node('month'), day__to__month))
    network.add_edge(Conversion(network.get_node('week'), network.get_node('day'), week__to__day))
    network.add_edge(Conversion(network.get_node('year'), network.get_node('month'), year__to__month))
    network.add_edge(Conversion(network.get_node('year'), network.get_node('day'), year__to__day))
    network.add_edge(Conversion(network.get_node('lustrum'), network.get_node('year'), lustrum__to__year))
    network.add_edge(Conversion(network.get_node('decade'), network.get_node('year'), decade__to__year))
    network.add_edge(Conversion(network.get_node('century'), network.get_node('year'), century__to__year))

    # Temperature conversions
    network.add_edge(Conversion(network.get_node('Celsius'), network.get_node('Kelvin'), Celsius__to__Kelvin))
    network.add_edge(Conversion(network.get_node('Kelvin'), network.get_node('Celsius'), Kelvin__to__Celsius))
    network.add_edge(Conversion(network.get_node('Celsius'), network.get_node('Fahrenheit'), Celsius__to__Fahrenheit))
    network.add_edge(
        Conversion(network.get_node('Fahrenheit'), network.get_node('Celsius'), Fahrenheit__to__Celsius))
    network.add_edge(Conversion(network.get_node('Fahrenheit'), network.get_node('Rankine'), Fahrenheit__to__Rankine))
    network.add_edge(Conversion(network.get_node('Rankine'), network.get_node('Fahrenheit'), Rankine__to__Fahrenheit))
    network.add_edge(Conversion(network.get_node('Rankine'), network.get_node('Kelvin'), Rankine__to__Kelvin))
    network.add_edge(Conversion(network.get_node('Kelvin'), network.get_node('Rankine'), Kelvin__to__Rankine))

    # Length conversions
    network.add_edge(Conversion(network.get_node('yard'), network.get_node('meter'), yard__to__meter))
    # network.addEdge(Conversion(network.getNode('foot'), network.getNode('meter'), foot__to__meter))
    network.add_edge(Conversion(network.get_node('inch'), network.get_node('thou'), inch__to__thou))
    network.add_edge(Conversion(network.get_node('inch'), network.get_node('tenth'), inch__to__tenth))
    network.add_edge(Conversion(network.get_node('foot'), network.get_node('inch'), foot__to__inch))
    network.add_edge(Conversion(network.get_node('yard'), network.get_node('foot'), yard__to__foot))
    network.add_edge(Conversion(network.get_node('chain'), network.get_node('yard'), chain__to__yard))
    network.add_edge(Conversion(network.get_node('furlong'), network.get_node('chain'), furlong__to__chain))
    network.add_edge(Conversion(network.get_node('mile'), network.get_node('furlong'), mile__to__furlong))
    network.add_edge(Conversion(network.get_node('league'), network.get_node('mile'), league__to__mile))
    network.add_edge(
        Conversion(network.get_node('nautical league'), network.get_node('nautical mile'), nautical_league__to__nautical_mile))
    network.add_edge(Conversion(network.get_node('nautical mile'), network.get_node('meter'), nautical_mile__to__meter))
    network.add_edge(Conversion(network.get_node('rod'), network.get_node('yard'), rod__to__yard))
    network.add_edge(Conversion(network.get_node('astronomical unit'), network.get_node('meter'), astronomical_unit__to__meter))
    network.add_edge(Conversion(network.get_node('parsec'), network.get_node('astronomical unit'), parsec__to__astronomical_unit))
    network.add_edge(Conversion(network.get_node('light year'), network.get_node('meter'), light_year__to__meter))
    network.add_edge(
        Conversion(network.get_node('scandinavian mile'), network.get_node('kilometer'), scandinavian_mile__to__kilometer))

    # Velocity conversion
    network.add_edge(Conversion(network.get_node('mile per hour'), network.get_node('kilometer per hour'),
                                mile_per_hour__to__kilometer_per_hour))

    # Area conversions
    network.add_edge(Conversion(network.get_node('square kilometer'), network.get_node('square meter'), square_kilometer__to__square_meter))
    network.add_edge(Conversion(network.get_node('square mile'), network.get_node('acre'), square_mile__to__acre))
    network.add_edge(Conversion(network.get_node('acre'), network.get_node('square yard'), acre__to__square_yard))
    network.add_edge(Conversion(network.get_node('square rod'), network.get_node('square yard'), square_rod__to__square_yard))
    network.add_edge(Conversion(network.get_node('square yard'), network.get_node('square foot'), square_yard__to__square_foot))
    network.add_edge(Conversion(network.get_node('square foot'), network.get_node('square inch'), square_foot__to__square_inch))
    network.add_edge(Conversion(network.get_node('square foot'), network.get_node('square meter'), square_foot__to__square_meter))
    network.add_edge(Conversion(network.get_node('square inch'), network.get_node('square thou'), square_inch__to__square_thou))
    network.add_edge(Conversion(network.get_node('square inch'), network.get_node('square tenth'), square_inch__to__square_tenth))
    network.add_edge(Conversion(network.get_node('square chain'), network.get_node('square yard'), square_chain__to__square_yard))
    network.add_edge(Conversion(network.get_node('square furlong'), network.get_node('square chain'), square_furlong__to__square_chain))
    network.add_edge(Conversion(network.get_node('square mile'), network.get_node('square furlong'), square_mile__to__square_furlong))
    network.add_edge(Conversion(network.get_node('square league'), network.get_node('square mile'), square_league__to__square_mile))

    network.add_edge(Conversion(network.get_node('Darcy'), network.get_node('µm2'), Darcy__to__µm2))


    # Volume conversions
    network.add_edge(Conversion(network.get_node('litre'), network.get_node('cubic centimeter'), litre__to__cubic_centimeter))
    network.add_edge(Conversion(network.get_node('gill'), network.get_node('fluid ounce'), gill__to__fluid_ounce))
    network.add_edge(Conversion(network.get_node('pint'), network.get_node('gill'), pint__to__gill))
    network.add_edge(Conversion(network.get_node('quart'), network.get_node('pint'), quart__to__pint))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('fluid ounce'), gallonUS__to__fluid_ounce))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('quart'), gallonUS__to__quart))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('cubic inch'), gallonUS__to__cubic_inch))

    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('quartUK'), gallonUK__to__quartUK))
    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('fluid ounce UK'), gallonUK__to__fluid_ounce_UK))
    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('litre'), gallonUK__to__litre))
    network.add_edge(Conversion(network.get_node('gillUK'), network.get_node('fluid ounce UK'), gillUK__to__fluid_ounce_UK))
    network.add_edge(Conversion(network.get_node('pintUK'), network.get_node('gillUK'), pintUK__to__gillUK))
    network.add_edge(Conversion(network.get_node('quartUK'), network.get_node('pintUK'), quartUK__to__pintUK))

    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('liter'), gallonUK__to__liter))
    network.add_edge(Conversion(network.get_node('cubic foot'), network.get_node('cubic meter'), cubic_foot__to__cubic_meter))
    network.add_edge(Conversion(network.get_node('standard cubic foot'), network.get_node('standard cubic meter'),
                                standard_cubic_foot__to__standard_cubic_meter))
    network.add_edge(Conversion(network.get_node('standard barrel'), network.get_node('USgal'), standard_barrel__to__USgal))
    network.add_edge(
        Conversion(network.get_node('standard cubic meter'), network.get_node('standard barrel'),
                   standard_cubic_meter__to__standard_barrel))
    network.add_edge(
        Conversion(network.get_node('standard barrel'), network.get_node('standard cubic foot'),
                   standard_barrel__to__standard_cubic_foot))
    network.add_edge(Conversion(network.get_node('reservoir cubic meter'), network.get_node('reservoir barrel'),
                                reservoir_cubic_meter__to__reservoir_barrel))
    network.add_edge(Conversion(network.get_node('reservoir cubic meter'), network.get_node('standard cubic meter'),
                                reservoir_cubic_meter__to__standard_cubic_meter))
    # network.addEdge(Conversion(network.getNode('standard cubic meter'), network.getNode('standard cubic foot'), standard_cubic_meter__to__standard_cubic_foot))

    network.add_edge(Conversion(network.get_node('cubic inch'), network.get_node('cubic thou'), cubic_inch__to__cubic_thou))
    network.add_edge(Conversion(network.get_node('cubic inch'), network.get_node('cubic tenth'), cubic_inch__to__cubic_tenth))
    network.add_edge(Conversion(network.get_node('cubic foot'), network.get_node('cubic inch'), cubic_foot__to__cubic_inch))
    network.add_edge(Conversion(network.get_node('cubic yard'), network.get_node('cubic foot'), cubic_yard__to__cubic_foot))
    network.add_edge(Conversion(network.get_node('cubic chain'), network.get_node('cubic yard'), cubic_chain__to__cubic_yard))
    network.add_edge(Conversion(network.get_node('cubic furlong'), network.get_node('cubic chain'), cubic_furlong__to__cubic_chain))
    network.add_edge(Conversion(network.get_node('cubic mile'), network.get_node('cubic furlong'), cubic_mile__to__cubic_furlong))
    network.add_edge(Conversion(network.get_node('cubic league'), network.get_node('cubic mile'), cubic_league__to__cubic_mile))

    # Pressure conversions
    network.add_edge(Conversion(network.get_node('psi gauge'), network.get_node('absolute psi'), psi_gauge__to__absolute_psi))
    network.add_edge(Conversion(network.get_node('absolute psi'), network.get_node('psi gauge'), absolute_psi__to__psi_gauge))
    network.add_edge(Conversion(network.get_node('bar gauge'), network.get_node('absolute bar'), bar_gauge__to__absolute_bar))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('bar gauge'), absolute_bar__to__bar_gauge))

    network.add_edge(
        Conversion(network.get_node('absolute bar'), network.get_node('absolute psi'), absolute_bar__to__absolute_psi))
    network.add_edge(
        Conversion(network.get_node('bar gauge'), network.get_node('psi gauge'), bar_gauge__to__psi_gauge))
    network.add_edge(Conversion(network.get_node('bar'), network.get_node('psi'), bar__to__psi))
    network.add_edge(Conversion(network.get_node('psi'), network.get_node('bar'), psi__to__bar))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('Pascal'), absolute_bar__to__Pascal))
    # network.addEdge(Conversion(network.getNode('atmosphere'), network.getNode('absolute bar'), atmosphere__to__absolute_bar))
    network.add_edge(Conversion(network.get_node('atmosphere'), network.get_node('Pascal'), atmosphere__to__Pascal))
    network.add_edge(Conversion(network.get_node('atmosphere'), network.get_node('Torr'), atmosphere__to__Torr))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('bar'), equality))
    network.add_edge(Conversion(network.get_node('absolute psi'), network.get_node('psi'), equality))
    network.add_edge(Conversion(network.get_node('bar gauge'), network.get_node('bar'), equality))
    network.add_edge(Conversion(network.get_node('psi gauge'), network.get_node('psi'), equality))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('kilogram/square centimeter'),
                                absolute_bar__to__kilogram_slash_square_centimeter))

    # Mass conversion
    network.add_edge(Conversion(network.get_node('grain'), network.get_node('milligrams'), grain__to__milligrams))
    network.add_edge(Conversion(network.get_node('pennyweight'), network.get_node('grain'), pennyweight__to__grain))
    network.add_edge(Conversion(network.get_node('dram'), network.get_node('pound'), dram__to__pound))
    network.add_edge(Conversion(network.get_node('stone'), network.get_node('pound'), stone__to__pound))
    network.add_edge(Conversion(network.get_node('quarter'), network.get_node('stone'), quarter__to__stone))
    network.add_edge(Conversion(network.get_node('weight ounce'), network.get_node('dram'), weight_ounce__to__dram))
    network.add_edge(Conversion(network.get_node('pound'), network.get_node('weight ounce'), pound__to__weight_ounce))
    network.add_edge(Conversion(network.get_node('long hundredweight'), network.get_node('quarter'), long_hundredweight__to__quarter))
    network.add_edge(Conversion(network.get_node('short hundredweight'), network.get_node('pound'), short_hundredweight__to__pound))
    network.add_edge(
        Conversion(network.get_node('short ton'), network.get_node('short hundredweight'), short_ton__to__short_hundredweight))
    network.add_edge(Conversion(network.get_node('long ton'), network.get_node('long hundredweight'), long_ton__to__long_hundredweight))

    network.add_edge(Conversion(network.get_node('metric ton'), network.get_node('kilogram'), metric_ton__to__kilogram))
    network.add_edge(Conversion(network.get_node('kilogram'), network.get_node('gram'), kilogram__to__gram))
    # network.addEdge(Conversion(network.getNode('pound'), network.getNode('gram'), pound__to__gram))
    network.add_edge(Conversion(network.get_node('pound'), network.get_node('kilogram'), pound__to__kilogram))

    # Force conversion
    network.add_edge(Conversion(network.get_node('kilogram mass'), network.get_node('kilogram force'),
                                kilogram_mass__to__kilogram_force))
    network.add_edge(Conversion(network.get_node('kilogram force'), network.get_node('kilogram mass'),
                                kilogram_force__to__kilogram_mass))
    network.add_edge(Conversion(network.get_node('Dyne'), network.get_node('Newton'), Dyne__to__Newton))
    network.add_edge(Conversion(network.get_node('Newton'), network.get_node('Dyne'), Newton__to__Dyne))
    network.add_edge(Conversion(network.get_node('pound force'), network.get_node('kilogram force'),
                                pound__to__kilogram))
    network.add_edge(Conversion(network.get_node('kilogram force'), network.get_node('Newton'),
                                kilogram_force__to__Newton))

    # Energy Conversion
    network.add_edge(Conversion(network.get_node('Joule'), network.get_node('gram calorie'), Joule__to__gram_calorie))
    network.add_edge(Conversion(network.get_node('Kilojoule'), network.get_node('Joule'), Kilojoule__to__Joule))
    network.add_edge(Conversion(network.get_node('Kilojoule'), network.get_node('kilowatt hour'), Kilojoule__to__kilowatt_hour))
    network.add_edge(
        Conversion(network.get_node('Kilojoule'), network.get_node('British thermal unit'), Kilojoule__to__British_thermal_unit))

    # Power conversion
    network.add_edge(Conversion(network.get_node('Horsepower'), network.get_node('Watt'), Horsepower__to__Watt))

    # Density conversion
    network.add_edge(Conversion(network.get_node('API'), network.get_node('SgO'), API__to__SgO))
    network.add_edge(Conversion(network.get_node('SgO'), network.get_node('API'), SgO__to__API))
    network.add_edge(Conversion(network.get_node('API'), network.get_node('g/cc'), API__to__g_slash_cc))
    network.add_edge(Conversion(network.get_node('g/cc'), network.get_node('API'), g_slash_cc__to__API))
    network.add_edge(Conversion(network.get_node('SgO'), network.get_node('g/cc'), equality))
    network.add_edge(Conversion(network.get_node('SgW'), network.get_node('g/cc'), equality))
    network.add_edge(Conversion(network.get_node('SgG'), network.get_node('kg/m3'), SgG__to__kg_slash_m3))
    network.add_edge(Conversion(network.get_node('psia/ft'), network.get_node('lb/ft3'), psia_slash_ft__to__lb_slash_ft3))
    network.add_edge(Conversion(network.get_node('psi/ft'), network.get_node('lb/ft3'), psi_slash_ft__to__lb_slash_ft3))
    network.add_edge(Conversion(network.get_node('psig/ft'), network.get_node('lb/ft3'), psig_slash_ft__to__lb_slash_ft3))
    network.add_edge(Conversion(network.get_node('bara/m'), network.get_node('kg/m3'), bara_slash_m__to__kg_slash_m3))
    network.add_edge(Conversion(network.get_node('bar/m'), network.get_node('kg/m3'), bar_slash_m__to__kg_slash_m3))
    network.add_edge(Conversion(network.get_node('barg/m'), network.get_node('kg/m3'), barg_slash_m__to__kg_slash_m3))
    network.add_edge(Conversion(network.get_node('g/cm3'), network.get_node('lb/ft3'), g_slash_cm3__to__lb_slash_ft3))
    network.add_edge(Conversion(network.get_node('lb/ft3'), network.get_node('lb/stb'), lb_slash_ft3__to__lb_slash_stb))

    # Viscosity conversions
    network.add_edge(Conversion(network.get_node('Pascal*second'), network.get_node('Poise'), Pascal_star_second__to__Poise))
    network.add_edge(Conversion(network.get_node('Pascal*second'), network.get_node('Reyn'), Pascal_star_second__to__Reyn))
    network.add_edge(Conversion(network.get_node('Pascal*second'), network.get_node('Poiseuille'), equality))

    # Data conversions
    network.add_edge(Conversion(network.get_node('byte'), network.get_node('bit'), byte__to__bit))

    for unit_kind in list(dictionary.keys()):
        if '_REVERSE' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                nameList = list(dictionary[unit_kind].keys())
            else:
                nameList = list(dictionary[unit_kind])
            for unit_name in nameList:
                for otherName in network.children_of(network.get_node(unit_name)):
                    if network.get_node(unit_name) != otherName:
                        network.add_edge(Conversion(otherName, network.get_node(unit_name),
                                                    network.edges[network.get_node(unit_name)][1][
                                                        network.edges[network.get_node(unit_name)][0].index(otherName)],
                                                    True))

    for unit_kind in list(dictionary.keys()):
        if '_FROMvolume' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            for unit_name in list(dictionary[unit_kind]):
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for otherName in network.children_of(network.get_node(unit_name.split('/')[0])):
                    if network.get_node(unit_name.split('/')[0]) != otherName:
                        logger.warning('R   3: ' + unit_name, otherName.get_name())
                        otherRate = otherName.get_name() + '/' + unit_name.split('/')[1]
                        network.add_node(UNode(otherRate))
                        network.add_edge(Conversion(network.get_node(unit_name), otherRate,
                                                    network.edges[network.get_node(unit_name.split('/')[1])][1][
                                                        network.edges[network.get_node(unit_name.split('/')[1])][
                                                            0].index(
                                                            otherName)]))
                        network.add_edge(Conversion(otherRate, network.get_node(unit_name),
                                                    network.edges[network.get_node(unit_name.split('/')[1])][1][
                                                        network.edges[network.get_node(unit_name.split('/')[1])][
                                                            0].index(
                                                            otherName)], True))

    to_remove = []
    for unit_kind in dictionary:
        if '_' in unit_kind:
            to_remove.append(unit_kind)
        else:  # if '_' not in unit_kind :
            dictionary[unit_kind] = tuple(set(dictionary[unit_kind]))
    for unit_kind in to_remove:
        dictionary.pop(unit_kind)
    # merge data dictionaries into a single
    dictionary['Data'] = tuple(dictionary['dataBYTE'] + dictionary['dataBIT'])
    del dictionary['dataBYTE']
    del dictionary['dataBIT']
    dictionary['UserUnits'] = list(dictionary['UserUnits'])
    return network


def _create_Rates() -> None:
    # volumes / Time
    rates = list(dictionary['Rate']) if 'Rate' in dictionary else []
    rates += [volume + '/' + time for volume in dictionary['Volume'] for time in dictionary['Time']]
    rates += [weight + '/' + time for weight in dictionary['Weight'] for time in dictionary['Time']]
    rates += [data + '/' + time for data in dictionary['Data'] for time in dictionary['Time']]
    dictionary['Rate'] = tuple(set(rates))


def _create_VolumeRatio() -> None:
    # Volume / Volume
    ratio = list(dictionary['VolumeRatio']) if 'VolumeRatio' in dictionary else []
    ratio += [numerator + '/' + denominator for numerator in dictionary['Volume'] for denominator in
              dictionary['Volume']]
    dictionary['VolumeRatio'] = tuple(set(ratio))


def _create_Density() -> None:
    # mass / Volume
    density = list(dictionary['Density']) if 'Density' in dictionary else []
    density += [mass + '/' + volume for mass in dictionary['Mass'] for volume in dictionary['Volume']]
    dictionary['Density'] = tuple(set(density))


def _create_Velocity() -> None:
    # Length / Time
    velocity = list(dictionary['Velocity']) if 'Velocity' in dictionary else []
    velocity += [length + '/' + time for length in dictionary['Length'] for time in dictionary['Time']]
    dictionary['Velocity'] = tuple(set(velocity))


def _create_Power() -> None:
    # Length / Time
    power = list(dictionary['Power']) if 'Power' in dictionary else []
    power += [energy + '/' + time for energy in dictionary['Energy'] for time in dictionary['Time']]
    power += [voltage + '*' + current for voltage in dictionary['Voltage'] for current in dictionary['Current']]
    power += [current + '*' + voltage for voltage in dictionary['Voltage'] for current in dictionary['Current']]
    power += [current + '2*' + resistance for resistance in dictionary['Resistance'] for current in dictionary['Current']]
    power += [resistance + '*' + current + '2' for resistance in dictionary['Resistance'] for current in dictionary['Current']]
    dictionary['Power'] = tuple(set(power))


def _create_Frequency() -> None:
    # 1 / Time
    frequency = list(dictionary['Frequency']) if 'Frequency' in dictionary else []
    frequency += ['1/' + time for time in dictionary['Time']]
    dictionary['Frequency'] = tuple(set(frequency))


def _create_Conductance() -> None:
    # 1 / Resistance
    conductance = list(dictionary['Conductance']) if 'Conductance' in dictionary else []
    conductance += ['1/' + resistance for resistance in dictionary['Resistance']]
    dictionary['Conductance'] = tuple(set(conductance))


def _create_Capacitance_Charge() -> None:
    # Capacitance, Charge = Charge / Voltage, Capacitance * Voltage
    capacitance, charge = \
        list(dictionary['Capacitance']) if 'Capacitance' in dictionary else [], \
        list(dictionary['Charge']) if 'Charge' in dictionary else []
    capacitance, charge, = \
        capacitance + \
        [charge + '/' + voltage for voltage in dictionary['Voltage'] for charge in dictionary['Charge']], \
        charge + \
        [capacitance + '*' + voltage for voltage in dictionary['Voltage'] for capacitance in dictionary['Capacitance']] + \
        [voltage + '*' + capacitance for voltage in dictionary['Voltage'] for capacitance in dictionary['Capacitance']]
    dictionary['Capacitance'] = tuple(set(capacitance))
    dictionary['Charge'] = tuple(set(charge))


def _create_Voltage_Current_Resistance() -> None:
    # Voltage, Current, Resistance = (Current * Resistance) + (Power / Current), \
    #                                (Voltage / Resistance) + (Power / Voltage), \
    #                                (Voltage / Current)
    voltage, current, resistance = \
        list(dictionary['Voltage']) if 'Voltage' in dictionary else [], \
        list(dictionary['Current']) if 'Current' in dictionary else [], \
        list(dictionary['Resistance']) if 'Resistance' in dictionary else []
    voltage, current, resistance = \
        voltage + \
        [current + '*' + resistance for resistance in dictionary['Resistance'] for current in dictionary['Current']] + \
        [resistance + '*' + current for resistance in dictionary['Resistance'] for current in dictionary['Current']] + \
        [power + '/' + current for power in dictionary['Power'] for current in dictionary['Current']], \
        current + \
        [voltage + '/' + resistance for resistance in dictionary['Resistance'] for voltage in dictionary['Voltage']] + \
        [power + '/' + voltage for power in dictionary['Power'] for voltage in dictionary['Voltage']], \
        resistance + \
        [voltage + '/' + current for current in dictionary['Current'] for voltage in dictionary['Voltage']]
    dictionary['Voltage'] = tuple(set(voltage))
    dictionary['Current'] = tuple(set(current))
    dictionary['Resistance'] = tuple(set(resistance))


def _create_Pressure() -> None:
    # Weight / Area
    pressure = list(dictionary['Pressure']) if 'Pressure' in dictionary else []
    pressure += [weight + '/' + area for weight in dictionary['Weight'] for area in dictionary['Area']]
    dictionary['Pressure'] = tuple(set(pressure))


def _create_ProductivityIndex() -> None:
    # Volume / Time / Pressure
    productivityIndex = list(dictionary['ProductivityIndex']) if 'ProductivityIndex' in dictionary else []
    productivityIndex += [volume + '/' + time + '/' + pressure
                          for volume in dictionary['Volume']
                          for time in dictionary['Time']
                          for pressure in dictionary['Pressure']]
    dictionary['ProductivityIndex'] = tuple(set(productivityIndex))


def _create_PressureGradient() -> None:
    # Pressure / Length
    pressureGradient = list(dictionary['PressureGradient']) if 'PressureGradient' in dictionary else []
    pressureGradient += [pressure + '/' + length for pressure in dictionary['Pressure'] for length in
                         dictionary['Length']]
    dictionary['PressureGradient'] = tuple(set(pressureGradient))


def _create_TemperatureGradient() -> None:
    # Pressure / Length
    temperatureGradient = list(dictionary['TemperatureGradient']) if 'TemperatureGradient' in dictionary else []
    temperatureGradient += [temperature + '/' + length for temperature in dictionary['Temperature'] for length in
                            dictionary['Length']]
    dictionary['TemperatureGradient'] = tuple(set(temperatureGradient))


def _create_Acceleration() -> None:
    # Length / Time / Time
    acceleration = list(dictionary['Acceleration']) if 'Acceleration' in dictionary else []
    acceleration += [(length + '/' + time1 + '2') if time1 == time2 else (length + '/' + time1 + '/' + time2)
                     for length in dictionary['Length']
                     for time1 in dictionary['Time']
                     for time2 in dictionary['Time']]
    dictionary['Acceleration'] = tuple(set(acceleration))


def _complete_products() -> None:
    for key in dictionary:
        dictionary[key] = tuple(set(list(dictionary[key]) + [(u.split('*')[1] + '*' + u.split('*')[0])
                                                             for u in dictionary[key]
                                                             if '/' not in u
                                                             and len(u.split('*')) == 2]))


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


# load the network into an instance of the graph database
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
    # load the dictionary with ratio units
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
    # clean empty edges
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

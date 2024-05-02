#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:36:48 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20240502
__all__ = ['units_network', 'network_to_frame', 'save_memory', 'load_memory', 'clean_memory', 'delete_cache']

import logging
import os

from .dictionaries import SI, SI_order, OGF, OGF_order, DATA, DATA_order, dictionary, StandardAirDensity, \
    StandardEarthGravity
from .network import UDigraph, UNode, Conversion
from .parameters import unyts_parameters_, dir_path
from os.path import isfile
from json import dump as json_dump

try:
    from cloudpickle import dump as cloudpickle_dump, load as cloudpickle_load
    _cloudpickle_ = True
except ModuleNotFoundError:
    if unyts_parameters_.cache_:
        logging.warning("Missing `cloudpickle` package. Not able to cache network dictionary.")
    _cloudpickle_ = False

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def save_memory(path=None) -> None:
    units_network.save_memory(path)


def load_memory(path=None) -> None:
    units_network.load_memory(path)


def clean_memory(path=None) -> None:
    units_network.clean_memory()


def delete_cache() -> None:
    for each in ('units/search_memory.cache', 'units/units_network.cache', 'units/units_dictionary.cache',
                 'units/temperature_ratio_conversions.cache', 'units/unitless_names.cache'):
        path = dir_path + each
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


def get_fvf() -> None:
    if units_network.fvf is not None:
        return str(round(units_network.fvf, 3))
    else:
        return ""


def _load_network():
    logging.info('preparing units network...')
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
                    network.add_edge(Conversion(network.get_node(secondName), network.get_node(unit_name), lambda x: x))
                    network.add_edge(Conversion(network.get_node(unit_name), network.get_node(secondName), lambda x: x))
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
                                       lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.replace(' ', rep)),
                                       lambda x: x))
                        if type(dictionary[unit_kind]) is dict:
                            for secondName in dictionary[unit_kind][unit_name]:
                                if ' ' in secondName:
                                    network.add_node(UNode(secondName))
                                    network.add_node(UNode(secondName.replace(' ', rep)))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName.replace(' ', rep)), network.get_node(secondName),
                                                   lambda x: x))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName), network.get_node(secondName.replace(' ', rep)),
                                                   lambda x: x))
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
                                                   lambda x: x))
                                    network.add_edge(
                                        Conversion(network.get_node(secondName), network.get_node(secondName.replace(' ', rep)),
                                                   lambda x: x))
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
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[1]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][1]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][1],
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_SI' in unit_kind and unit_kind.split('_')[0] in SI_order[2]:
            for unit_name in dictionary[unit_kind]:
                network.add_node(UNode(unit_name))
                dictionary[unit_kind.split('_')[0]].append(unit_name)
                for prefix in SI:
                    network.add_node(UNode(prefix + unit_name))
                    network.add_edge(
                        Conversion(network.get_node(prefix + unit_name), network.get_node(unit_name), SI[prefix][2]))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(prefix + unit_name), SI[prefix][2],
                                   True))
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
                                   True))
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
                                   True))
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
                                   True))
                    dictionary[unit_kind.split('_')[0]].append(prefix + unit_name)
        if '_PLURALwS' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name + 's'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name + 's'), lambda x: x))
                    network.add_edge(
                        Conversion(network.get_node(unit_name + 's'), network.get_node(unit_name), lambda x: x))
                    dictionary[unit_kind.split('_')[0]].append(unit_name + 's')
            else:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name + 's'))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name + 's'), lambda x: x))
                    network.add_edge(
                        Conversion(network.get_node(unit_name + 's'), network.get_node(unit_name), lambda x: x))
                    dictionary[unit_kind.split('_')[0]].append(unit_name + 's')
            if '_UPPER' in unit_kind:
                if type(dictionary[unit_kind]) is dict:
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.upper() + 'S'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.upper() + 'S'),
                                       lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.upper() + 'S'), network.get_node(unit_name),
                                       lambda x: x))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.upper() + 'S')
                else:
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.upper() + 'S'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.upper() + 'S'),
                                       lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.upper() + 'S'), network.get_node(unit_name),
                                       lambda x: x))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.upper() + 'S')
            if '_LOWER' in unit_kind:
                if type(dictionary[unit_kind]) is dict:
                    # list_names = list(dictionary[unit_kind].keys())
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.lower() + 's'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.lower() + 's'),
                                       lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.lower() + 's'), network.get_node(unit_name),
                                       lambda x: x))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.lower() + 's')
                else:
                    for unit_name in dictionary[unit_kind]:
                        network.add_node(UNode(unit_name))
                        network.add_node(UNode(unit_name.lower() + 's'))
                        network.add_edge(
                            Conversion(network.get_node(unit_name), network.get_node(unit_name.lower() + 's'),
                                       lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(unit_name.lower() + 's'), network.get_node(unit_name),
                                       lambda x: x))
                        dictionary[unit_kind.split('_')[0]].append(unit_name.lower() + 's')
        if '_UPPER' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.upper()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.upper()), lambda x: x))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.upper()), network.get_node(unit_name), lambda x: x))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.upper())
                    for secondName in dictionary[unit_kind][unit_name]:
                        network.add_node(UNode(secondName))
                        network.add_node(UNode(secondName.upper()))
                        network.add_edge(
                            Conversion(network.get_node(secondName), network.get_node(secondName.upper()), lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(secondName.upper()), network.get_node(secondName), lambda x: x))
                        dictionary[unit_kind.split('_')[0]].append(secondName.upper())
            else:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.upper()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.upper()), lambda x: x))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.upper()), network.get_node(unit_name), lambda x: x))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.upper())
        if '_LOWER' in unit_kind:
            if type(dictionary[unit_kind]) is dict:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.lower()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.lower()), lambda x: x))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.lower()), network.get_node(unit_name), lambda x: x))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.lower())
                    for secondName in dictionary[unit_kind][unit_name]:
                        network.add_node(UNode(secondName))
                        network.add_node(UNode(secondName.lower()))
                        network.add_edge(
                            Conversion(network.get_node(secondName), network.get_node(secondName.lower()), lambda x: x))
                        network.add_edge(
                            Conversion(network.get_node(secondName.lower()), network.get_node(secondName), lambda x: x))
                        dictionary[unit_kind.split('_')[0]].append(secondName.lower())
            else:
                for unit_name in dictionary[unit_kind]:
                    network.add_node(UNode(unit_name))
                    network.add_node(UNode(unit_name.lower()))
                    network.add_edge(
                        Conversion(network.get_node(unit_name), network.get_node(unit_name.lower()), lambda x: x))
                    network.add_edge(
                        Conversion(network.get_node(unit_name.lower()), network.get_node(unit_name), lambda x: x))
                    dictionary[unit_kind.split('_')[0]].append(unit_name.lower())
        if '_INVERSE' in unit_kind:
            pass

    # Percentage & fraction :
    network.add_edge(Conversion(network.get_node('fraction'), network.get_node('percentage'), lambda x: x * 100))
    network.add_edge(Conversion(network.get_node('percentage'), network.get_node('fraction'), lambda p: p / 100))

    # Time conversions
    # network.addEdge(Conversion(network.getNode('second'), network.getNode('millisecond'), lambda t: t*1000))
    network.add_edge(Conversion(network.get_node('minute'), network.get_node('second'), lambda t: t * 60))
    network.add_edge(Conversion(network.get_node('hour'), network.get_node('minute'), lambda t: t * 60))
    network.add_edge(Conversion(network.get_node('day'), network.get_node('hour'), lambda t: t * 24))
    network.add_edge(Conversion(network.get_node('day'), network.get_node('month'), lambda t: t / 365.25 * 12))
    network.add_edge(Conversion(network.get_node('week'), network.get_node('day'), lambda t: t * 7))
    network.add_edge(Conversion(network.get_node('year'), network.get_node('month'), lambda t: t * 12))
    network.add_edge(Conversion(network.get_node('year'), network.get_node('day'), lambda t: t * 36525 / 100))
    network.add_edge(Conversion(network.get_node('lustrum'), network.get_node('year'), lambda t: t * 5))
    network.add_edge(Conversion(network.get_node('decade'), network.get_node('year'), lambda t: t * 10))
    network.add_edge(Conversion(network.get_node('century'), network.get_node('year'), lambda t: t * 100))

    # Temperature conversions
    network.add_edge(Conversion(network.get_node('Celsius'), network.get_node('Kelvin'), lambda t: t + 273.15))
    network.add_edge(Conversion(network.get_node('Kelvin'), network.get_node('Celsius'), lambda t: t - 273.15))
    network.add_edge(Conversion(network.get_node('Celsius'), network.get_node('Fahrenheit'), lambda t: t * 9 / 5 + 32))
    network.add_edge(
        Conversion(network.get_node('Fahrenheit'), network.get_node('Celsius'), lambda t: (t - 32) * 5 / 9))
    network.add_edge(Conversion(network.get_node('Fahrenheit'), network.get_node('Rankine'), lambda t: t + 459.67))
    network.add_edge(Conversion(network.get_node('Rankine'), network.get_node('Fahrenheit'), lambda t: t - 459.67))
    network.add_edge(Conversion(network.get_node('Rankine'), network.get_node('Kelvin'), lambda t: t * 5 / 9))
    network.add_edge(Conversion(network.get_node('Kelvin'), network.get_node('Rankine'), lambda t: t * 9 / 5))

    # Length conversions
    network.add_edge(Conversion(network.get_node('yard'), network.get_node('meter'), lambda d: d * 9144 / 10000))
    # network.addEdge(Conversion(network.getNode('foot'), network.getNode('meter'), lambda d: d*0.3048))
    network.add_edge(Conversion(network.get_node('inch'), network.get_node('thou'), lambda d: d * 1000))
    network.add_edge(Conversion(network.get_node('inch'), network.get_node('tenth'), lambda d: d * 10))
    network.add_edge(Conversion(network.get_node('foot'), network.get_node('inch'), lambda d: d * 12))
    network.add_edge(Conversion(network.get_node('yard'), network.get_node('foot'), lambda d: d * 3))
    network.add_edge(Conversion(network.get_node('chain'), network.get_node('yard'), lambda d: d * 22))
    network.add_edge(Conversion(network.get_node('furlong'), network.get_node('chain'), lambda d: d * 10))
    network.add_edge(Conversion(network.get_node('mile'), network.get_node('furlong'), lambda d: d * 8))
    network.add_edge(Conversion(network.get_node('league'), network.get_node('mile'), lambda d: d * 3))
    network.add_edge(
        Conversion(network.get_node('nautical league'), network.get_node('nautical mile'), lambda d: d * 3))
    network.add_edge(Conversion(network.get_node('nautical mile'), network.get_node('meter'), lambda d: d * 1852))
    network.add_edge(Conversion(network.get_node('rod'), network.get_node('yard'), lambda d: d * 55 / 10))

    # Area conversions
    network.add_edge(Conversion(network.get_node('square mile'), network.get_node('acre'), lambda d: d * 640))
    network.add_edge(Conversion(network.get_node('acre'), network.get_node('square yard'), lambda d: d * 4840))
    network.add_edge(
        Conversion(network.get_node('square rod'), network.get_node('square yard'), lambda d: d * 3025 / 100))
    network.add_edge(Conversion(network.get_node('square yard'), network.get_node('square foot'), lambda d: d * 9))
    network.add_edge(Conversion(network.get_node('square foot'), network.get_node('square inch'), lambda d: d * 144))
    network.add_edge(Conversion(network.get_node('square foot'), network.get_node('square meter'),
                                lambda d: d * (3048 ** 2) / (10000 ** 2)))
    # network.add_edge(Conversion(network.get_node('Darcy'), network.get_node('mD'), lambda d: d * 1000))
    network.add_edge(Conversion(network.get_node('Darcy'), network.get_node('µm2'), lambda d: d * 0.9869233))
    # network.addEdge(Conversion(network.getNode('m*m'), network.getNode('m'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('m'), network.getNode('m*m'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('rd*rd'), network.getNode('rd'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('rd'), network.getNode('rd*rd'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('yd*yd'), network.getNode('yd'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('yd'), network.getNode('yd*yd'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('ft*ft'), network.getNode('ft'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('ft'), network.getNode('ft*ft'), lambda d: d**2))
    # network.addEdge(Conversion(network.getNode('in*in'), network.getNode('in'), lambda d: d**0.5))
    # network.addEdge(Conversion(network.getNode('in'), network.getNode('in*in'), lambda d: d**2))

    # Volume conversions
    network.add_edge(Conversion(network.get_node('gill'), network.get_node('fluid ounce'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('pint'), network.get_node('gill'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('quart'), network.get_node('pint'), lambda v: v * 2))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('fluid ounce'), lambda v: v * 128))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('quart'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('gallonUS'), network.get_node('cubic inch'), lambda v: v * 231))

    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('quartUK'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('fluid ounce UK'), lambda v: v * 160))
    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('litre'), lambda v: v * 4.54609))
    network.add_edge(Conversion(network.get_node('gillUK'), network.get_node('fluid ounce UK'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('pintUK'), network.get_node('gillUK'), lambda v: v * 4))
    network.add_edge(Conversion(network.get_node('quartUK'), network.get_node('pintUK'), lambda v: v * 2))

    network.add_edge(Conversion(network.get_node('gallonUK'), network.get_node('liter'), lambda v: v * 4.54609))
    network.add_edge(Conversion(network.get_node('cubic foot'), network.get_node('cubic meter'),
                                lambda v: v * (3048 ** 3) / (10000 ** 3)))
    network.add_edge(Conversion(network.get_node('standard cubic foot'), network.get_node('standard cubic meter'),
                                lambda v: v * (3048 ** 3) / (10000 ** 3)))
    network.add_edge(Conversion(network.get_node('standard barrel'), network.get_node('USgal'), lambda v: v * 42))
    network.add_edge(
        Conversion(network.get_node('standard cubic meter'), network.get_node('standard barrel'),
                   lambda v: v * 6.289814))
    network.add_edge(
        Conversion(network.get_node('standard barrel'), network.get_node('standard cubic foot'),
                   lambda v: v * 5.614584))
    network.add_edge(Conversion(network.get_node('reservoir cubic meter'), network.get_node('reservoir barrel'),
                                lambda v: v * 6.289814))
    network.add_edge(Conversion(network.get_node('reservoir cubic meter'), network.get_node('standard cubic meter'),
                                lambda v: v / network.get_fvf()))
    # network.addEdge(Conversion(network.getNode('standard cubic meter'), network.getNode('standard cubic foot'), lambda v: v/5.614584))

    # Pressure conversions
    network.add_edge(Conversion(network.get_node('psi gauge'), network.get_node('absolute psi'), lambda p: p + 14.6959))
    network.add_edge(Conversion(network.get_node('absolute psi'), network.get_node('psi gauge'), lambda p: p - 14.6959))
    network.add_edge(Conversion(network.get_node('bar gauge'), network.get_node('absolute bar'), lambda p: p + 1.01325))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('bar gauge'), lambda p: p - 1.01325))

    network.add_edge(
        Conversion(network.get_node('absolute bar'), network.get_node('absolute psi'), lambda p: p * 14.50377377322))
    network.add_edge(
        Conversion(network.get_node('bar gauge'), network.get_node('psi gauge'), lambda p: p * 14.50377377322))
    network.add_edge(Conversion(network.get_node('bar'), network.get_node('psi'), lambda p: p * 14.50377377322))
    network.add_edge(Conversion(network.get_node('psi'), network.get_node('bar'), lambda p: p / 14.50377377322))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('Pascal'), lambda p: p * 100000))
    # network.addEdge(Conversion(network.getNode('atmosphere'), network.getNode('absolute bar'), lambda p: p*1.01325))
    network.add_edge(Conversion(network.get_node('atmosphere'), network.get_node('Pascal'), lambda p: p * 101325))
    network.add_edge(Conversion(network.get_node('atmosphere'), network.get_node('Torr'), lambda p: p * 760))
    network.add_edge(Conversion(network.get_node('absolute bar'), network.get_node('bar'), lambda p: p))
    network.add_edge(Conversion(network.get_node('absolute psi'), network.get_node('psi'), lambda p: p))
    network.add_edge(Conversion(network.get_node('bar gauge'), network.get_node('bar'), lambda p: p))
    network.add_edge(Conversion(network.get_node('psi gauge'), network.get_node('psi'), lambda p: p))

    # mass Conversion
    network.add_edge(Conversion(network.get_node('grain'), network.get_node('milligrams'), lambda w: w * 64.7989))
    network.add_edge(Conversion(network.get_node('pennyweight'), network.get_node('grain'), lambda w: w * 24))
    network.add_edge(Conversion(network.get_node('dram'), network.get_node('pound'), lambda w: w / 256))
    network.add_edge(Conversion(network.get_node('stone'), network.get_node('pound'), lambda w: w * 14))
    network.add_edge(Conversion(network.get_node('quarter'), network.get_node('stone'), lambda w: w * 2))
    network.add_edge(Conversion(network.get_node('weight ounce'), network.get_node('dram'), lambda w: w * 16))
    network.add_edge(Conversion(network.get_node('pound'), network.get_node('weight ounce'), lambda w: w * 16))
    network.add_edge(Conversion(network.get_node('long hundredweight'), network.get_node('quarter'), lambda w: w * 4))
    network.add_edge(Conversion(network.get_node('short hundredweight'), network.get_node('pound'), lambda w: w * 100))
    network.add_edge(
        Conversion(network.get_node('short ton'), network.get_node('short hundredweight'), lambda w: w * 20))
    network.add_edge(Conversion(network.get_node('long ton'), network.get_node('long hundredweight'), lambda w: w * 20))

    network.add_edge(Conversion(network.get_node('metric ton'), network.get_node('kilogram'), lambda w: w * 1000))
    network.add_edge(Conversion(network.get_node('kilogram'), network.get_node('gram'), lambda w: w * 1000))
    # network.addEdge(Conversion(network.getNode('pound'), network.getNode('gram'), lambda w: w*453.59237))
    network.add_edge(
        Conversion(network.get_node('pound'), network.get_node('kilogram'), lambda w: w * 45359237 / 100000000))

    # force Conversion
    # network.addEdge(Conversion(network.getNode('kilogram'), network.getNode('kilogram force'), lambda f: f* converter(StandardEarthGravity,'m/s2','cm/s2',False)))
    network.add_edge(Conversion(network.get_node('kilogram mass'), network.get_node('kilogram force'),
                                lambda f: f * StandardEarthGravity))
    network.add_edge(Conversion(network.get_node('kilogram force'), network.get_node('kilogram mass'),
                                lambda f: f / StandardEarthGravity))
    network.add_edge(Conversion(network.get_node('Dyne'), network.get_node('Newton'), lambda f: f * 1E-5))
    network.add_edge(Conversion(network.get_node('Newton'), network.get_node('Dyne'), lambda f: f * 1E5))

    # Energy Conversion
    network.add_edge(Conversion(network.get_node('Joule'), network.get_node('gram calorie'), lambda e: e / 4.184))
    network.add_edge(Conversion(network.get_node('Kilojoule'), network.get_node('Joule'), lambda e: e * 1000))
    network.add_edge(Conversion(network.get_node('Kilojoule'), network.get_node('kilowatt hour'), lambda e: e / 3600))
    network.add_edge(
        Conversion(network.get_node('Kilojoule'), network.get_node('British thermal unit'), lambda e: e / 1.055))

    # Power Conversion
    network.add_edge(Conversion(network.get_node('Horsepower'), network.get_node('Watt'), lambda e: e * 745.699872))

    # Density Conversion
    network.add_edge(Conversion(network.get_node('API'), network.get_node('SgO'), lambda d: 141.5 / (131.5 + d)))
    network.add_edge(Conversion(network.get_node('SgO'), network.get_node('API'), lambda d: 141.5 / d - 131.5))
    network.add_edge(Conversion(network.get_node('API'), network.get_node('g/cc'), lambda d: 141.5 / (131.5 + d)))
    network.add_edge(Conversion(network.get_node('g/cc'), network.get_node('API'), lambda d: 141.5 / d - 131.5))
    network.add_edge(Conversion(network.get_node('SgO'), network.get_node('g/cc'), lambda d: d))
    network.add_edge(Conversion(network.get_node('SgW'), network.get_node('g/cc'), lambda d: d))
    network.add_edge(Conversion(network.get_node('SgG'), network.get_node('kg/m3'), lambda d: d * StandardAirDensity))
    network.add_edge(Conversion(network.get_node('psia/ft'), network.get_node('lb/ft3'), lambda d: d * 144))
    network.add_edge(
        Conversion(network.get_node('g/cm3'), network.get_node('lb/ft3'), lambda d: d * 62.427960576144606))
    network.add_edge(Conversion(network.get_node('lb/ft3'), network.get_node('lb/stb'), lambda d: d * 5.614584))

    # viscosity conversions
    network.add_edge(Conversion(network.get_node('Pa*s'), network.get_node('Poise'), lambda v: v * 10))

    # data conversions
    network.add_edge(Conversion(network.get_node('byte'), network.get_node('bit'), lambda d: d * 8))

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
                        logging.warning('R   3: ' + unit_name, otherName.get_name())
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
    logging.warning('Rebuilding units dictionary...')
    from .dictionaries import _load_dictionary
    dictionary, temperatureRatioConversions, unitless_names = _load_dictionary()
    units_network = _load_network()
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


# load the network into an instance of the graph database
if not unyts_parameters_.reload_ and \
        isfile(dir_path + 'units/units_network.cache') and \
        (not _cloudpickle_ or (_cloudpickle_ and isfile(dir_path + 'units/units_dictionary.cache'))) and \
        isfile(dir_path + 'units/temperature_ratio_conversions.cache') and \
        isfile(dir_path + 'units/unitless_names.cache'):
    try:
        with open(dir_path + 'units/units_network.cache', 'rb') as f:
            units_network = cloudpickle_load(f)
        logging.info('units network loaded from cache...')
        unyts_parameters_.reload_ = False
        unyts_parameters_.save_params()
    except:
        logging.error("Failed to load from cache. Creating new dictionaries and saving them to cache...")
        units_network, dictionary, temperatureRatioConversions, unitless_names = _rebuild_units()
else:
    units_network = _load_network()
    # load the dictionary with ratio unis
    _create_Rates()
    _create_VolumeRatio()
    _create_Density()
    _create_Velocity()
    _create_Acceleration()
    _create_ProductivityIndex()
    _create_PressureGradient()
    _create_TemperatureGradient()
    _create_Power()
    _create_Frequency()
    _create_Conductance()
    _create_Capacitance_Charge()
    _create_Voltage_Current_Resistance()
    _complete_products()

    unyts_parameters_.reload_ = False
    unyts_parameters_.save_params()
    if unyts_parameters_.cache_:
        logging.info('saving units network and dictionary to cache...')
        if _cloudpickle_:
            with open(dir_path + 'units/units_network.cache', 'wb') as f:
                cloudpickle_dump(units_network, f)
        with open(dir_path + 'units/units_dictionary.cache', 'w') as f:
            json_dump(dictionary, f)

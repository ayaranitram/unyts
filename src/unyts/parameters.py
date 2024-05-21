#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.5'
__release__ = 20240510
__all__ = ['unyts_parameters_', 'print_path', 'reload', 'raise_error', 'cache', 'dir_path', 'set_density']

import logging
import os.path
from json import load as json_load, dump as json_dump
from os.path import isfile
from pathlib import Path
from sys import getrecursionlimit

ini_path = Path(__file__).with_name('parameters.ini').absolute()
dir_path = os.path.dirname(ini_path) + '/'
off_switches = ('off', 'no', 'not', '')
__max_recursion_default__ = 25

class UnytsParameters(object):
    """
    class to load the user preferences
    """

    def __init__(self, reload=None) -> None:
        self.print_path_ = False
        self.cache_ = True
        self.raise_error_ = True
        self.verbose_ = False
        self.reduce_parentheses_ = True
        self.show_version_ = True
        self.density_ = None
        self.max_recursion_ = __max_recursion_default__
        self.load_params()
        self.reload_ = self.reload_ if reload is None else bool(reload)
        self.memory_ = not self.reload_

    def load_params(self) -> None:
        if isfile(ini_path):
            with open(ini_path, 'r') as f:
                params = json_load(f)
        else:
            params = {'print_path_': False,
                      'cache_': True,
                      'reload_': True,
                      'raise_error_': True,
                      'verbose_': False,
                      'reduce_parentheses_': True,
                      'show_version_': False,
                      'max_recursion_': __max_recursion_default__}
            with open(ini_path, 'w') as f:
                json_dump(params, f)
        self.print_path_ = params['print_path_']
        self.cache_ = params['cache_']
        self.reload_ = params['reload_']
        self.raise_error_ = params['raise_error_']
        self.verbose_ = params['verbose_']
        self.reduce_parentheses_ = params['reduce_parentheses_']
        self.show_version_ = params['show_version_']
        self.max_recursion_ = params['max_recursion_'] if 'max_recursion_' in params else __max_recursion_default__

    def save_params(self) -> None:
        params = {'print_path_': self.print_path_,
                  'cache_': self.cache_,
                  'reload_': self.reload_,
                  'raise_error_': self.raise_error_,
                  'verbose_': self.verbose_,
                  'reduce_parentheses_': self.verbose_,
                  'show_version_': self.show_version_,
                  'max_recursion_': self.max_recursion_}
        with open(ini_path, 'w') as f:
            json_dump(params, f)

    def print_path(self, switch=None) -> None:
        if switch is None:
            self.print_path_ = not self.print_path_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.print_path_ = False
            else:
                self.print_path_ = True
        else:
            self.print_path_ = bool(switch)
        logging.info(f"print path {'ON' if self.print_path_ else 'OFF'}")
        self.save_params()

    def cache(self, switch=None) -> None:
        if switch is None:
            self.cache_ = not self.cache_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.cache_ = False
            else:
                self.cache_ = True
        else:
            self.cache_ = bool(switch)
        logging.info(f"cache {'ON' if self.cache_ else 'OFF'}")
        self.save_params()

    def raise_error(self, switch=None) -> None:
        if switch is None:
            self.raise_error_ = not self.raise_error_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.raise_error_ = False
            else:
                self.raise_error_ = True
        else:
            self.raise_error_ = bool(switch)
        logging.info(f"raise_error {'ON' if self.raise_error_ else 'OFF'}")
        self.save_params()

    def verbose(self, switch=None) -> None:
        if switch is None:
            self.verbose_ = not self.verbose_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.verbose_ = False
            else:
                self.verbose_ = True
        else:
            self.verbose_ = bool(switch)
        logging.info(f"verbose {'ON' if self.verbose_ else 'OFF'}")
        self.save_params()

    def reload_next_time(self, switch=None):
        if switch is None:
            self.reload_ = not self.reload_
        elif type(switch) is str:
            if switch.lower().strip() in off_switches:
                self.reload_ = False
            else:
                self.reload_ = True
        else:
            self.reload_ = bool(switch)
        if self.reload_:
            logging.info("Unyts will recreate dictionaries next time.")
        else:
            logging.info("Unyts will try to load dictionaries from cache next time.")
        self.save_params()

    def recursion_limit(self, limit=None):
        if limit is None:
            return self.max_recursion_
        elif limit.lower() == 'max' or limit is False:
            self.max_recursion_ = getrecursionlimit() - 15
            return self.max_recursion_
        elif limit is True:
            self.max_recursion_ = __max_recursion_default__
            return self.max_recursion_
        elif type(limit) is int:
            self.max_recursion_ = min(limit, getrecursionlimit() - 15)
        else:
            raise ValueError(f"not valid recursion limit, must be an integer of False.")


unyts_parameters_ = UnytsParameters()


def print_path(switch=None) -> None:
    unyts_parameters_.print_path(switch)


def raise_error(switch=None) -> None:
    unyts_parameters_.raise_error(switch)


def verbose(switch=None) -> None:
    unyts_parameters_.verbose(switch)


def cache(switch=None) -> None:
    unyts_parameters_.cache(switch)

def recursion_limit(limit=None) -> int:
    return unyts_parameters_.recursion_limit(limit)


def set_density(density: float, units: str = 'g/cc') -> None:
    from .units.ratios import Density
    if not isinstance(density, (int, float)) and not type(density) is Density:
        raise ValueError("'density' must be a float or int.")
    elif type(density) is Density:
        density = density.to('g/cc')
        density, units = density.value, density.unit
    if units.lower() not in ('g/cc', 'g/cm3'):
        from .converter import convert
        from .errors import NoConversionFoundError
        try:
            density = convert(density, units, 'g/cc')
        except NoConversionFoundError:
            raise ValueError("density 'units' are not valid.")
        if density is None:
            raise ValueError("density 'units' are not valid.")
    unyts_parameters_.density_ = density


def _get_density() -> float:
    while unyts_parameters_.density_ is None:
        density = input("Please set density value: ")
        try:
            density = float(density)
            unyts_parameters_.density_ = density
        except ValueError:
            print("'density' must be float or int.")
            density = None
    return unyts_parameters_.density_


def get_density():
    from .units.ratios import Density
    if unyts_parameters_.density_ is None:
        raise ValueError("'density' is not set.")
    return Density(unyts_parameters_.density_, 'g/cc')


def reload() -> None:
    unyts_parameters_.reload_ = True
    unyts_parameters_.save_params()
    logging.info("On next 'import unyts', the dictionary and network will be re-created.\n It might be required to restart the Python kernel.")

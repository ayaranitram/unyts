#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.1'
__release__ = 20230106
__all__ = ['unyts_parameters_', 'print_path', 'reload', 'raise_error', 'cache']

import os.path
from json import load as json_load, dump as json_dump
from os.path import isfile
from pathlib import Path

ini_path = Path(__file__).with_name('parameters.ini').absolute()
dir_path = os.path.dirname(ini_path) + '/'
off_switches = ('off', 'no', 'not', '')


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
        self.load_params()
        self.reload_ = self.reload_ if reload is None else bool(reload)

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
                      'show_version_': False}
            with open(ini_path, 'w') as f:
                json_dump(params, f)
        self.print_path_ = params['print_path_']
        self.cache_ = params['cache_']
        self.reload_ = params['reload_']
        self.raise_error_ = params['raise_error_']
        self.verbose_ = params['verbose_']
        self.reduce_parentheses_ = params['reduce_parentheses_']
        self.show_version_ = params['show_version_']

    def save_params(self) -> None:
        params = {'print_path_': self.print_path_,
                  'cache_': self.cache_,
                  'reload_': self.reload_,
                  'raise_error_': self.raise_error_,
                  'verbose_': self.verbose_,
                  'reduce_parentheses_': self.verbose_,
                  'show_version_': self.show_version_}
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
        print("print_path", "ON" if self.print_path_ else "OFF")

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
        print("cache", "ON" if self.cache_ else "OFF")

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
        print("raise_error", "ON" if self.raise_error_ else "OFF")

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
        print("verbose", "ON" if self.verbose_ else "OFF")


unyts_parameters_ = UnytsParameters()


def print_path(switch=None) -> None:
    unyts_parameters_.print_path(switch)


def raise_error(switch=None) -> None:
    unyts_parameters_.raise_error(switch)


def verbose(switch=None) -> None:
    unyts_parameters_.verbose(switch)


def cache(switch=None) -> None:
    unyts_parameters_.cache(switch)


def reload() -> None:
    unyts_parameters_.reload_ = True
    unyts_parameters_.save_params()
    print("On next 'import unyts', the dictionary and network will be re-created.",
          'It might be required to restart the Python kernel.', sep='\n')

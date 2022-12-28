#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.6'
__release__ = 20221228
__all__ = ['unyts_parameters_', 'print_path', 'dir_path', 'reload', 'raise_error']

import os.path
from json import load, dump
from os.path import isfile
from pathlib import Path

ini_path = Path(__file__).with_name('parameters.ini').absolute()
dir_path = os.path.dirname(ini_path) + '/'


class UnytsParameters(object):
    """
    class to load the user preferences
    """

    def __init__(self, reload=None) -> None:
        self.print_path_ = False
        self.cache_ = True
        self.load_params()
        self.reload_ = self.reload_ if reload is None else bool(reload)
        self.raise_error_ = True

    def load_params(self) -> None:
        if isfile(ini_path):
            with open(ini_path, 'r') as f:
                params = load(f)
        else:
            params = {'print_path_': False,
                      'cache_': True,
                      'reload_': True,
                      'raise_error_': True}
            with open(ini_path, 'w') as f:
                dump(params, f)
        self.print_path_ = params['print_path_']
        self.cache_ = params['cache_']
        self.reload_ = params['reload_']
        self.raise_error_ = params['raise_error_']

    def save_params(self) -> None:
        params = {'print_path_': self.print_path_,
                  'cache_': self.cache_,
                  'reload_': self.reload_,
                  'raise_error_': self.raise_error_}
        with open(ini_path, 'w') as f:
            dump(params, f)

    def print_path(self, switch=None) -> None:
        if switch is None:
            self.print_path_ = not self.print_path_
        elif type(switch) is str:
            if switch.lower().strip()[:2] in ('of', 'no', 'fa', ''):
                self.print_path_ = False
            else:
                self.print_path_ = True
        else:
            self.print_path_ = bool(switch)
        print("print_path", "ON" if self.print_path_ else "OFF")


    def raise_error(self, switch=None) -> None:
        if switch is None:
            self.raise_error_ = not self.raise_error_
        elif type(switch) is str:
            if switch.lower().strip()[:2] in ('of', 'no', 'fa', ''):
                self.raise_error_ = False
            else:
                self.raise_error_ = True
        else:
            self.raise_error_ = bool(switch)
        print("raise_error", "ON" if self.raise_error_ else "OFF")


unyts_parameters_ = UnytsParameters()


def print_path(switch=None) -> None:
    unyts_parameters_.print_path(switch)


def raise_error(switch=None) -> None:
    unyts_parameters_.raise_error(switch)


def reload() -> None:
    unyts_parameters_.reload_ = True
    unyts_parameters_.save_params()
    print("On next 'import unyts', the dictionary and network will be re-created.",
          'It might be required to restart the Python kernel.', sep='\n')

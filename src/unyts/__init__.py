#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.8.12'
__release__ = 20240526
__all__ = ['units', 'convert', 'convertible', 'Unit', 'is_Unit',
           'set_unit', 'set_conversion', 'set_density', 'get_density'
           'save', 'start_gui', 'set_fvf']

from .parameters import unyts_parameters_, print_path, reload, raise_error, cache, set_density, get_density, recursion_limit
from .database import network_to_frame, save_memory, load_memory, set_fvf
from .units.define import units
from .converter import convert, convertible
from .Empty import Empty
from .unit_class import Unit, is_Unit
from .units.custom import set_unit, set_conversion
from .gui import start_gui


if unyts_parameters_.show_version_:
    print(f"loaded unyts version {str(__version__)}")
    unyts_parameters_.show_version_ = False
    unyts_parameters_.save_params()

from .unitary import *


def save(path=None) -> None:
    """
    Will save the current state of searches memory to a cache file that will be loaded next time unyts is started.

    Returns
    -------
    None
    """
    save_memory(path)


def load(path=None) -> None:
    """
    Will load the saved cache searches into current memory of the converter.

    Returns
    -------
    None
    """
    load_memory(path)

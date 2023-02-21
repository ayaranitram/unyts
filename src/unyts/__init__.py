#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.20'
__release__ = 20230221
__all__ = ['units', 'convert', 'Unit', 'is_Unit', 'set_unit', 'set_conversion', 'convertible', 'save']

# import unyts.parameters
from .parameters import unyts_parameters_, print_path, reload, raise_error, cache
from .database import network_to_frame, save_memory, load_memory
from .units.define import units
from .converter import convert, convertible
from .unit_class import Unit, is_Unit
from .units.custom import set_unit, set_conversion

if unyts_parameters_.show_version_:
    print("loaded unyts version", __version__)
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

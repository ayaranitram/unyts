#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.12'
__release__ = 2023025
__all__ = ['units', 'convert', 'Unit', 'is_Unit', 'set_unit', 'set_conversion', 'convertible']

# import unyts.parameters
from .parameters import unyts_parameters_, print_path, reload, raise_error, cache
from .database import network_to_frame
from .units.define import units
from .converter import convert, convertible
from .unit_class import Unit, is_Unit
from .units.custom import set_unit, set_conversion

if unyts_parameters_.show_version_:
    print("loaded unyts version", __version__)
    # unyts_parameters_.show_version_ = False
    #unyts_parameters_.save_params()

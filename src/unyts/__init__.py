#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.8'
__release__ = 2023018
__all__ = ['units', 'convert', 'Unit', 'is_Unit']

import unyts.parameters
from unyts.parameters import print_path, reload, raise_error, cache
from unyts.units.define import units
from unyts.converter import convert
from unyts.unit_class import Unit, is_Unit

if unyts.parameters.unyts_parameters_.show_version_:
    print("loaded unyts version", __version__)
    unyts.parameters.unyts_parameters_.show_version_ = False
    unyts.parameters.unyts_parameters_.save_params()

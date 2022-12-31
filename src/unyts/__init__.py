#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.0'
__release__ = 20221231
__all__ = ['units', 'convert']

import unyts.parameters
from .parameters import print_path, reload, raise_error, cache
from .units.define import units
from .converter import convert
from .unit_class import Unit

if unyts.parameters.unyts_parameters_.show_version_:
    print("loaded unyts version", __version__)
    unyts.parameters.unyts_parameters_.show_version_ = False
    unyts.parameters.unyts_parameters_.save_params()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: martin
"""

__version__ = '0.1.7'
__release__ = 20220813

# from .units.custom import *
from .units.define import units
from ._convert import convertUnit
from ._convert import convertUnit as convert
from ._database import unitsNetwork

def print_path(switch):
    if type(switch) is str and switch.lower().strip() == 'off':
        switch = False
    unitsNetwork.print = bool(switch)
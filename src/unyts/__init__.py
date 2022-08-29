#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.2.5'
__release__ = 20220830

# from .units.custom import *
from .units.define import units
#from ._convert import convertUnit
#from ._convert import convertUnit_old as convert_old  # mainteined while testing
from ._convert import convertUnit as convert

def print_path(switch=None):
    from ._database import unitsNetwork
    if type(switch) is str and switch.lower().strip() == 'off':
        switch = False
    elif type(switch) is str:
        unitsNetwork.print = bool(switch)
    else:
        unitsNetwork.print = False if unitsNetwork.print is True else True
        
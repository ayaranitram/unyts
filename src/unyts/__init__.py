#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.4'
__release__ = 20220924
__all__ = ['units', 'convert']


from .units.define import units
from .convert import convertUnit
from .convert import convertUnit as convert
from .unit_class import unit

def print_path(switch=None):
    from ._database import unitsNetwork
    if type(switch) is str and switch.lower().strip() == 'off':
        switch = False
    elif type(switch) is str:
        unitsNetwork.print = bool(switch)
    else:
        unitsNetwork.print = False if unitsNetwork.print is True else True
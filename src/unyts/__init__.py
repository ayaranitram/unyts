#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: martin
"""

__version__ = '0.1.5'
__release__ = 20220803

from .units import *
from ._convert import convertUnit
from ._convert import convertUnit as convert
from ._database import unitsNetwork

def print_path(switch):
    if type(switch) is str and switch.lower().strip() == 'off':
        switch = False
    unitsNetwork.print = bool(switch)
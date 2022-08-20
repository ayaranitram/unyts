#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:10:14 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__all__ = ['WrongUnits','WrongValue']
__version__ = '0.0.20-10-24'

class WrongUnits(Exception):
    def __init__(self,message='unit not listed in library, unit must be a string'):
        print('ERROR: Wrong Units, ' + message)


class WrongValue(Exception):
    def __init__(self,message='value unit must be a float or integer'):
        print('ERROR: Wrong Value, ' + message)
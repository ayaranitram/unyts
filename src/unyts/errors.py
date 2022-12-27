#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:10:14 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.5'
__release__ = 20221226
__all__ = ['WrongUnitsError', 'WrongValueError', 'NoConversionFoundError']


class WrongUnitsError(Exception):
    def __init__(self, message='Unit not listed in library, Unit must be a string.'):
        self.message = 'ERROR: Wrong Units, ' + message


class WrongValueError(Exception):
    def __init__(self, message='value Unit must be a float or integer.'):
        self.message = 'ERROR: Wrong Value, ' + message


class NoConversionFoundError(Exception):
    def __init__(self, message='for the provided units.'):
        self.message = 'ERROR: Conversion path not found, ' + message

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:10:14 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.8'
__release__ = 20240811
__all__ = ['WrongUnitsError', 'WrongValueError', 'NoConversionFoundError', 'NoFVFError']


class WrongUnitsError(Exception):
    def __init__(self, message='unit not listed in library. Unit must be a valid string, Unit instance or Unit class.'):
        self.message = 'ERROR: Wrong Units, ' + message


class WrongValueError(Exception):
    def __init__(self, message='value must be a float, integer, complex or numeric array.'):
        self.message = 'ERROR: Wrong Value, ' + message


class NoConversionFoundError(Exception):
    def __init__(self, message='for the provided units.'):
        self.message = 'ERROR: Conversion path not found ' + message


class NoFVFError(Exception):
    def __init__(self):
        self.message = 'ERROR: FVF constant not defined'

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:10:14 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['WrongUnitsError', 'WrongValueError', 'NoConversionFoundError']


class WrongUnitsError(Exception):
    def __init__(self, message='unit not listed in library, unit must be a string.'):
        self.message = 'ERROR: Wrong Units, ' + message


class WrongValueError(Exception):
    def __init__(self, message='value unit must be a float or integer.'):
        self.message = 'ERROR: Wrong Value, ' + message


class NoConversionFoundError(Exception):
    def __init__(self, message='for the provided units.'):
        self.message = 'ERROR: Conversion path not found, ' + message
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:10:14 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20250504
__all__ = ['WrongUnitsError', 'WrongValueError', 'NoConversionFoundError', 'NoFVFError', 'SearchTimeoutError']


class WrongUnitsError(Exception):
    def __init__(self, message='unit not listed in library. Unit must be a valid string, Unit instance or Unit class.'):
        self.message = f"ERROR: Wrong Units, {message}"


class WrongValueError(Exception):
    def __init__(self, message='value must be a float, integer, complex or numeric array.'):
        self.message = f"ERROR: Wrong Value, {message}"


class WrongDateFormatError(Exception):
    def __init__(self, message='value must be (single value or array) number or string representing a date.'):
        self.message = f"ERROR: Wrong Value, {message}"


class NoConversionFoundError(Exception):
    def __init__(self, message='for the provided units.'):
        self.message = f"ERROR: Conversion path not found {message}"


class NoFVFError(Exception):
    def __init__(self):
        self.message = "ERROR: FVF constant not defined"


class SearchTimeoutError(Exception):
    def __init__(self, message='The conversion exceeded the timeout limit of {unyts_parameters_.get_timeout()} seconds.'):
        if message is None:
            self.message = 'ERROR: The conversion exceeded the timeout limit. '
        elif type(message) is int:
            self.message = f"ERROR: The conversion exceeded the timeout limit of {message} seconds."
        else:
            self.message = f"{message}"

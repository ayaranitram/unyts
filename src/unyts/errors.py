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
    """Error raised when the provided units are invalid or not recognized."""
    def __init__(self, message='unit not listed in library. Unit must be a valid string, Unit instance or Unit class.'):
        """Initialize the WrongUnitsError with a descriptive message."""
        self.message = f"ERROR: Wrong Units, {message}"


class WrongValueError(Exception):
    """Error raised when the provided value is invalid or not recognized."""
    def __init__(self, message='value must be a float, integer, complex or numeric array.'):
        """Initialize the WrongValueError with a descriptive message."""
        self.message = f"ERROR: Wrong Value, {message}"


class WrongDateFormatError(Exception):
    """Error raised when the provided date format is invalid or not recognized."""
    def __init__(self, message='value must be (single value or array) number or string representing a date.'):
        """Initialize the WrongDateFormatError with a descriptive message."""
        self.message = f"ERROR: Wrong Date Format, {message}"


class NoConversionFoundError(Exception):
    """Error raised when no conversion path is found for the provided units."""
    def __init__(self, message='for the provided units.'):
        """Initialize the NoConversionFoundError with a descriptive message."""
        self.message = f"ERROR: Conversion path not found {message}"


class NoFVFError(Exception):
    """Error raised when the FVF constant is not defined."""
    def __init__(self):
        """Initialize the NoFVFError with a descriptive message."""
        self.message = "ERROR: FVF constant not defined"


class SearchTimeoutError(Exception):
    """Error raised when the conversion exceeds the timeout limit."""
    def __init__(self, message='The conversion exceeded the timeout limit of {unyts_parameters_.get_timeout()} seconds.'):
        """Initialize the SearchTimeoutError with a descriptive message."""
        if message is None:
            self.message = 'ERROR: The conversion exceeded the timeout limit. '
        elif type(message) is int:
            self.message = f"ERROR: The conversion exceeded the timeout limit of {message} seconds."
        else:
            self.message = f"{message}"

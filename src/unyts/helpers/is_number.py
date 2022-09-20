# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:18:15 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>

helper functions for units modules
"""

__version__ = '0.4.0'
__release__ = 20220920
__all__ = ['is_number']


def is_number(string):
    """
    Checks if a string represents a number.
    Valid numbers are:
        positive integers, as in .isnumeric() and .isdigit() methods from string class
        floats, numbers with pointsç
        negative numbers, with dash at the left of the digits
        complex numbers,

    Parameters
    ----------
    string : str
        the string to check if represents a numbers

    Returns
    -------
    True or False

    """
    try:
        complex(string)
        return True
    except:
        return False
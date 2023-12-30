# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:18:15 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>

helper functions for units modules
"""

__version__ = '0.4.7'
__release__ = 20221229
__all__ = ['is_number']


def is_number(string: str) -> bool:
    """
    Checks if a string represents a number.
    Valid numbers are:
        positive integers, as in .isnumeric() and .isdigit() methods from string class
        floats, numbers with dot
        negative numbers, with hyphen at the left of the digits
        complex numbers, a tuple of two numbers, the first one for the 'real' part
            and the second one for the imaginary part.

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
    except ValueError:
        return False

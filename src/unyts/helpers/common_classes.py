#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.1'
__release__ = 20230106
__all__ = ['array_like', 'number', 'numeric', 'unit_or_str']

from typing import Union
from unyts.unit_class import Unit
try:
    from numpy import ndarray
    _numpy_ = True
except ModuleNotFoundError:
    _numpy_ = False
try:
    from pandas import Series, DataFrame
    _pandas_ = True
except ModuleNotFoundError:
    _pandas_ = False


number = (int, float, complex)
unit_or_str = (Unit, str)


if _numpy_ and _pandas_:
    numeric = (int, float, complex, ndarray, Series, DataFrame)
    array_like = (ndarray, Series, DataFrame)
elif _numpy_:
    numeric = (int, float, complex, ndarray)
    array_like = (ndarray,)
elif _pandas_:
    numeric = (int, float, complex, Series, DataFrame)
    array_like = (Series, DataFrame)
else:
    numeric = (int, float, complex)
    array_like = tuple()
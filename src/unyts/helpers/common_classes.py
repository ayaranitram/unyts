#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.7'
__release__ = 20231230
__all__ = ['array_like', 'number', 'numeric',
           'array_like_', 'number_', 'numeric_',
           'unit_or_str', 'Empty', 'str_Empty']

from typing import Union
from ..unit_class import Unit
from ..Empty import Empty, str_Empty

unit_or_str = Union[str, Unit]

try:
    from numpy import ndarray, int64, float64, int32, float32

    _numpy_ = True
except ModuleNotFoundError:
    _numpy_ = False
try:
    from pandas import Series, DataFrame

    _pandas_ = True
except ModuleNotFoundError:
    _pandas_ = False

if _numpy_ and _pandas_:
    number_ = (int, float, complex, int32, int64, float32, float64)
    number = Union[int, float, complex, int32, int64, float32, float64]
    numeric_ = (int, float, complex, int32, int64, float32, float64, ndarray, Series, DataFrame)
    numeric = Union[int, float, complex, int32, int64, float32, float64, ndarray, Series, DataFrame]
    array_like_ = (ndarray, Series, DataFrame)
    array_like = Union[ndarray, Series, DataFrame]
elif _numpy_:
    number_ = (int, float, complex, int32, int64, float32, float64)
    number = Union[int, float, complex, int32, int64, float32, float64]
    numeric_ = (int, float, complex, ndarray, int32, int64, float32, float64)
    numeric = Union[int, float, complex, ndarray, int32, int64, float32, float64]
    array_like_ = (ndarray, )
    array_like = ndarray
elif _pandas_:
    number_ = (int, float, complex)
    number = Union[int, float, complex]
    numeric_ = (int, float, complex, Series, DataFrame)
    numeric = Union[int, float, complex, Series, DataFrame]
    array_like_ = (Series, DataFrame)
    array_like = Union[Series, DataFrame]
else:
    number_ = (int, float, complex)
    number = Union[int, float, complex]
    numeric_ = (int, float, complex)
    numeric = Union[int, float, complex]
    array_like_ = (None, )
    array_like = None

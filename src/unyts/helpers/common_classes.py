#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['array_like', 'number', 'numeric', 'unit_or_str']

from numpy import ndarray
from typing import Union
from unyts.unit_class import Unit

try:
    from pandas import Series, DataFrame
    array_like = tuple([ndarray, Series, DataFrame])
    numeric = Union[int, float, complex, ndarray, Series, DataFrame]
except ModuleNotFoundError:
    array_like = tuple([ndarray])
    numeric = Union[int, float, complex, ndarray]
number = Union[int, float, complex]
unit_or_str = Union[Unit, str]

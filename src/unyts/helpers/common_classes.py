#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.7'
__release__ = 20221229
__all__ = ['array_like', 'number', 'numeric', 'unit_or_str']

from numpy import ndarray
from typing import Union
from pandas import Series, DataFrame
from ..unit_class import Unit

array_like = tuple([ndarray, Series, DataFrame])
numeric = Union[int, float, complex, ndarray, Series, DataFrame]
number = Union[int, float, complex]
unit_or_str = Union[Unit, str]

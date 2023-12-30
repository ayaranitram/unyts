"""
Created on Sat Dec 30 22:27:33 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.0.0'
__release__ = 20231230
__all__ = ['Empty', 'str_Empty', 'str_Empty_']

from typing import Union


class EmptyType(type):
    def __repr__(self):
        return "Empty"


class Empty(object, metaclass=EmptyType):
    """
    A class to specify an "Empty" (not Null nor None) value.
    """


str_Empty = Union[str, Empty]
str_Empty_ = (str, Empty)

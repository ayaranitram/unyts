"""
Created on Sat Dec 30 22:27:33 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.1.0'
__release__ = 20250504
__all__ = ['Empty', 'str_Empty', 'str_Empty_', 'EmptyClass']

from typing import Union


class EmptyType(type):
    def __repr__(self):
        return "EmptyType"


class EmptyClass(object, metaclass=EmptyType):
    """
    A class to specify an "Empty" (not Null nor None) value.
    """
    def __repr__(self):
        return "Empty"

Empty = EmptyClass()

str_Empty = Union[str, EmptyClass]
str_Empty_ = (str, EmptyClass)

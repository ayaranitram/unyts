# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:27:57 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.helpers.is_number import is_number

def test_is_number():
    assert is_number(1) is True
    assert is_number(0) is True
    assert is_number(-1) is True
    assert is_number(1.0) is True
    assert is_number(-1.0) is True
    assert is_number('1') is True
    assert is_number('-1') is True
    assert is_number('1.0') is True
    assert is_number('-1.0') is True
    assert is_number('1+1j') is True
    assert is_number('-1+1j') is True
    assert is_number('-1-1j') is True
    assert is_number('A') is False
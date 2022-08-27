# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:27:57 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts._helpers._isnumber import isnumber

def test_isnumber():
    assert isnumber(1) is True
    assert isnumber(0) is True
    assert isnumber(-1) is True
    assert isnumber(1.0) is True
    assert isnumber(-1.0) is True
    assert isnumber('1') is True
    assert isnumber('-1') is True
    assert isnumber('1.0') is True
    assert isnumber('-1.0') is True
    assert isnumber('1+1j') is True
    assert isnumber('-1+1j') is True
    assert isnumber('-1-1j') is True
    assert isnumber('A') is False

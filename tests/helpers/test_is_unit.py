# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.helpers.is_unit import is_unit


def test_is_unit():
    assert is_unit('m') is True
    assert is_unit('m/h') is True
    assert is_unit('stb/day/psi') is True
    assert is_unit('bu') is False


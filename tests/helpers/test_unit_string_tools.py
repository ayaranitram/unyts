# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.helpers.unit_string_tools import split_ratio, split_product, split_unit, reduce_parentheses, reduce_units


def test_split_ratio():
    """Validate ratio splitting behavior for slash-separated unit strings."""
    assert split_ratio('m') == ['m']
    assert split_ratio('m/g') == ['m', 'g']
    assert split_ratio('m/g/s') == ['m', 'g', 's']
    assert split_ratio('m/g*s') == ['m', 'g*s']


def test_split_product():
    """Validate product splitting behavior for star-separated unit strings."""
    assert split_product('m') == ['m']
    assert split_product('m*g') == ['m', 'g']
    assert split_product('m*g*s') == ['m', 'g', 's']
    assert split_product('m*g/s') == ['m', 'g/s']


def test_split_unit():
    """Validate generic unit splitting into terms and operators."""
    assert split_unit('m') == ['m']
    assert split_unit('m/h') == ['m', '/', 'h']
    assert split_unit('mD*ft') == ['mD', '*', 'ft']


def test_remove_parenthesis():
    """Ensure redundant parentheses are flattened while preserving meaning."""
    assert reduce_parentheses('stb') == 'stb'
    assert reduce_parentheses('stb/day') == 'stb/day'
    assert reduce_parentheses('m*cm') == 'm*cm'
    assert reduce_parentheses('m*(in*ft)') == 'm*in*ft'
    assert reduce_parentheses('kg*(m/s)') == 'kg*m/s'
    assert reduce_parentheses('stb/(day*psi)') == 'stb/day/psi'
    assert reduce_parentheses('(stb/day)/(psi*ft2)') == 'stb/day/psi/ft2'
    assert reduce_parentheses('stb/(day*psi)*day') == 'stb/day/psi*day'
    assert reduce_parentheses('stb/(day/(psi*in2))') == 'stb/day*psi*in2'
    assert reduce_parentheses('stb/(day/(psi/in2))') == 'stb/day*psi/in2'


def test_reduce_units():
    """Ensure algebraic cancellation works for repeated unit factors."""
    assert reduce_units('m') == 'm'
    assert reduce_units('m/h') == 'm/h'
    assert reduce_units('m/h*h') == 'm'
    assert reduce_units('m/h/m') == '1/h'

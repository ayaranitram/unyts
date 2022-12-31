# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.helpers.unit_string_tools import _split_ratio, _split_product, _split_unit, _reduce_parentheses


def test__split_ratio():
    assert _split_ratio('m') == ('m',)
    assert _split_ratio('m/g') == ('m', 'g')
    assert _split_ratio('m/g/s') == ('m', 'g', 's')
    assert _split_ratio('m/g*s') == ('m', 'g*s')


def test__split_product():
    assert _split_product('m') == ('m',)
    assert _split_product('m*g') == ('m', 'g')
    assert _split_product('m*g*s') == ('m', 'g', 's')
    assert _split_product('m*g/s') == ('m', 'g/s')


def test__remove_parenthesis():
    assert _reduce_parentheses('stb') == 'stb'
    assert _reduce_parentheses('stb/day') == 'stb/day'
    assert _reduce_parentheses('m*cm') == 'm*cm'
    assert _reduce_parentheses('m*(in*ft)') == 'm*in*ft'
    assert _reduce_parentheses('kg*(m/s)') == 'kg*m/s'
    assert _reduce_parentheses('stb/(day*psi)') == 'stb/day/psi'
    assert _reduce_parentheses('(stb/day)/(psi*ft2)') == 'stb/day/psi/ft2'
    assert _reduce_parentheses('stb/(day*psi)*day') == 'stb/day/psi*day'
    assert _reduce_parentheses('stb/(day/(psi*in2))') == 'stb/day*psi*in2'
    assert _reduce_parentheses('stb/(day/(psi/in2))') == 'stb/day*psi/in2'

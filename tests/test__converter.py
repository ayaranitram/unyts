# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts import convert
from pandas import read_excel
from math import isnan
from unyts.converter import _clean_print_conversion_path, _split_ratio, _split_product, _reduce_parentheses


def test__clean_print_conversion_path():
    assert _clean_print_conversion_path() in (True, False)
    assert _clean_print_conversion_path(True) is True
    assert _clean_print_conversion_path(False) is False
    assert _clean_print_conversion_path(1) is True
    assert _clean_print_conversion_path(0) is False


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
    assert _reduce_parentheses('stb') == 'a'
    assert _reduce_parentheses('stb/day') == 'stb/day'
    assert _reduce_parentheses('m*cm') == 'm*cm'
    assert _reduce_parentheses('m*(in*ft)') == 'm*in*ft'
    assert _reduce_parentheses('kg*(m/s)') == 'kg*m/s'
    assert _reduce_parentheses('stb/(day*psi)') == 'stb/day/psi'
    assert _reduce_parentheses('(stb/day)/(psi*ft2)') == 'stb/dat/psi/ft2'
    assert _reduce_parentheses('stb/(day*psi)*day') == 'stb/day/psi*day'
    assert _reduce_parentheses('stb/(day/(psi*in2))') == 'stb/day*psi*in2'
    assert _reduce_parentheses('stb/(day/(psi/in2))') == 'stb/day*psi/in2'


def test_converter():
    data = read_excel('./tests/conversions_check.xlsx')
    error = 1E-4
    for i in data.index:
        if not isnan(data.loc[i, 'out']):
            print(data.loc[i, 'id'], ': converting', data.loc[i, 'source'], 'into', data.loc[i, 'target'])
            result = convert(data.loc[i, 'in'], data.loc[i, 'source'], data.loc[i, 'target'])
            print(result, data.loc[i, 'out'])
            assert abs(1 - result / data.loc[i, 'out']) < error

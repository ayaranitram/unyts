# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts import convert
from pandas import read_excel
from math import isnan
from unyts.converter import _apply_conversion, _get_conversion, _converter, _clean_print_conversion_path, convert_for_SimPandas, convertible
from unyts.database import units_network as UnNe
import numpy as np


def test__get_conversion():
    assert _get_conversion(3, 'meter', 'meter') == (3, [UnNe.get_node('meter')])
    assert _get_conversion('16/06/1969', 'date', 'DATE') == ('16/06/1969', [UnNe.get_node('date'), UnNe.get_node('DATE')])
    assert _get_conversion(2, 'foot', None) == (2, [])
    assert _get_conversion(3, None, 'meter') == (3, [])
    assert _get_conversion(4, None, None) == (4, [None])
    assert _get_conversion(5, 'fraction', 'meter') == (5, [])
    assert _get_conversion(0.25, 'fraction', 'percent') == (25.0, ['*', 100])
    assert _get_conversion(0.25, 'percent', 'fraction') == (0.0025, ['/', 100])
    assert _get_conversion(0.25, 'dimensionless', 'fraction') == (0.25, [])
    assert _get_conversion(0.01, 'F/ft', 'C/m') == (0.018226888305628464, ['*', 0.5555555555555556, '/', 1,
                                                                           UnNe.get_node('ft'),
                                                                           UnNe.get_node('foot'),
                                                                           UnNe.get_node('yard'),
                                                                           UnNe.get_node('meter'),
                                                                           UnNe.get_node('m')])
    assert _get_conversion(0.33, 'fraction', 'ft/ft') == (0.33, [])
    assert _get_conversion(0.33, 'ft3/ft3', 'fraction') == (0.33, [])
    assert _get_conversion(10, 'scf/stb', 'stb/scf') == (1/10, ['1/'])
    assert _get_conversion(1, 'm', 'cm') == (100, [UnNe.get_node('m'), UnNe.get_node('cm')])
    assert _get_conversion(1, 'meter', 'inch') == (39.37007874015748,
                                                   [UnNe.get_node('meter'),
                                                    UnNe.get_node('yard'),
                                                    UnNe.get_node('foot'),
                                                    UnNe.get_node('inch')])


def test__converter():
    assert _converter(0.433, 'psi/ft', 'bar/m') == (0.09794717545606699, [UnNe.get_node('psi'),
                                                                          UnNe.get_node('bar'),
                                                                          '/', 1,
                                                                          UnNe.get_node('ft'),
                                                                          UnNe.get_node('foot'),
                                                                          UnNe.get_node('yard'),
                                                                          UnNe.get_node('meter'),
                                                                          UnNe.get_node('m')])


def test__apply_conversion():
    conv, conv_path = _get_conversion(3, 'meter', 'meter')
    assert _apply_conversion(3, conv_path) == conv

    conv, conv_path = _get_conversion(0.25, 'fraction', 'percent')
    assert _apply_conversion(0.25, conv_path) == conv

    conv, conv_path = _get_conversion(0.25, 'percent', 'fraction')
    assert _apply_conversion(0.25, conv_path) == conv

    conv, conv_path = _get_conversion(0.25, 'dimensionless', 'fraction')
    assert _apply_conversion(0.25, conv_path) == conv

    conv, conv_path = _get_conversion(10, 'scf/stb', 'stb/scf')
    assert _apply_conversion(10, conv_path) == conv

    conv, conv_path = _get_conversion(0.01, 'F/ft', 'C/m')
    assert _apply_conversion(0.01, conv_path) == conv

    conv, conv_path = _get_conversion(1, 'meter', 'inch')
    assert _apply_conversion(1, conv_path) == conv

    conv, conv_path = _get_conversion(0.433, 'psi/ft', 'bar/m')
    assert round(_apply_conversion(0.433, conv_path), 6) == round(conv, 6)


def test__clean_print_conversion_path():
    assert _clean_print_conversion_path() in (True, False)
    assert _clean_print_conversion_path(True) is True
    assert _clean_print_conversion_path(False) is False
    assert _clean_print_conversion_path(1) is True
    assert _clean_print_conversion_path(0) is False


def test_convert():
    data = read_excel('./tests/conversions_check.xlsx')
    error = 1E-4
    for i in data.index:
        if not isnan(data.loc[i, 'out']):
            print(data.loc[i, 'id'], ': converting', data.loc[i, 'source'], 'into', data.loc[i, 'target'])
            result = convert(data.loc[i, 'in'], data.loc[i, 'source'], data.loc[i, 'target'], False)
            print(result, data.loc[i, 'out'])
            assert abs(1 - result / data.loc[i, 'out']) < error


def test_convert_for_SimPandas():
    array = np.random.rand(10)
    assert (convert_for_SimPandas(array, 'meter', 'litre') == array).all()
    assert (convert_for_SimPandas(array, 'm', 'yd') == convert(array, 'm', 'yd')).all()

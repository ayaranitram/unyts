# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

import unyts
from unyts import convert
from pandas import read_excel
from math import isnan


def test_converter():
    data = read_excel('./tests/conversions_check.xlsx')
    error = 1E-4
    for i in data.index:
        if not isnan(data.loc[i, 'out']):
            print(data.loc[i, 'id'], ': converting', data.loc[i, 'source'], 'into', data.loc[i, 'target'])
            result = convert(data.loc[i, 'in'], data.loc[i, 'source'], data.loc[i, 'target'])
            print(result, data.loc[i, 'out'])
            assert abs(1 - result / data.loc[i, 'out']) < error

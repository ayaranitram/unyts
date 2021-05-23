# -*- coding: utf-8 -*-
"""
Created on Sun May 23 09:56:26 2021

@author: martin
"""

from units._operations import unitBasePower

def test_unitBasePower():
    assert unitBasePower('m') == ('m', 1)
    assert unitBasePower('ft') == ('ft', 1)
    assert unitBasePower('m2') == ('m', 2)
    assert unitBasePower('ft3') == ('ft', 3)
    assert unitBasePower('1/m') == ('m', -1)
    assert unitBasePower('1/ft') == ('ft', -1)
    assert unitBasePower('day-1') == ('day', -1)
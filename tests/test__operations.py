# -*- coding: utf-8 -*-
"""
Created on Sun May 23 09:56:26 2021

@author: martin
"""

from unyts._operations import unitBasePower, unitProduct, unitDivision

def test_unitBasePower():
    assert unitBasePower('m') == ('m', 1)
    assert unitBasePower('ft') == ('ft', 1)
    assert unitBasePower('m2') == ('m', 2)
    assert unitBasePower('ft3') == ('ft', 3)
    assert unitBasePower('1/m') == ('m', -1)
    assert unitBasePower('1/ft') == ('ft', -1)
    assert unitBasePower('day-1') == ('day', -1)
    
def test_unitProduct():
    assert unitProduct('m','ft') == 'm2'
    assert unitProduct('ft','m') == 'ft2'
    assert unitProduct('m','s') == 'm*s'
    assert unitProduct('in2','in') == 'in3'
    
def test_unitDivision():
    assert unitDivision('m','m') == 'm/m'
    assert unitDivision('m','m2') == 'm-1'
    assert unitDivision('cm3','cm') == 'cm2'
    
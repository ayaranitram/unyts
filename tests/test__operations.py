# -*- coding: utf-8 -*-
"""
Created on Sun May 23 09:56:26 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.operations import unitBasePower, unitProduct, unitDivision, unitPower

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

def test_unitPower():
    assert unitPower('m', -1) == 'm-1'
    assert unitPower('m', 0) == 'dimensionless'
    assert unitPower('m', 1) == 'm'
    assert unitPower('m', 2) == 'm2'
    assert unitPower('m', 3) == 'm3'
    assert unitPower('ft2', -1) == 'ft-2'
    assert unitPower('ft2', 0) == 'dimensionless'
    assert unitPower('ft2', 1) == 'ft2'
    assert unitPower('ft2', 2) == 'ft4'
    assert unitPower('ft2', 3) == 'ft6'
    assert unitPower('s', 's') == 's^s'
    assert unitPower('m', 's') == 'm^s'
    assert unitPower('m2', 'm') == 'm^2m'
    assert unitPower('m2', 'm2') == 'm^4m'
# -*- coding: utf-8 -*-
"""
Created on Sun May 23 09:56:26 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.operations import unit_base_power, unit_product, unit_division, unit_power


def test_unit_base_power():
    assert unit_base_power('m') == ('m', 1)
    assert unit_base_power('ft') == ('ft', 1)
    assert unit_base_power('m2') == ('m', 2)
    assert unit_base_power('ft3') == ('ft', 3)
    assert unit_base_power('1/m') == ('m', -1)
    assert unit_base_power('1/ft') == ('ft', -1)
    assert unit_base_power('day-1') == ('day', -1)


def test_unit_product():
    assert unit_product('m', 'ft') == 'm2'
    assert unit_product('ft', 'm') == 'ft2'
    assert unit_product('m', 's') == 'm*s'
    assert unit_product('in2', 'in') == 'in3'


def test_unit_division():
    assert unit_division('m', 'm') == 'm/m'
    assert unit_division('m', 'm2') == 'm-1'
    assert unit_division('cm3', 'cm') == 'cm2'


def test_unit_power():
    assert unit_power('m', -1) == 'm-1'
    assert unit_power('m', 0) == 'Dimensionless'
    assert unit_power('m', 1) == 'm'
    assert unit_power('m', 2) == 'm2'
    assert unit_power('m', 3) == 'm3'
    assert unit_power('ft2', -1) == 'ft-2'
    assert unit_power('ft2', 0) == 'Dimensionless'
    assert unit_power('ft2', 1) == 'ft2'
    assert unit_power('ft2', 2) == 'ft4'
    assert unit_power('ft2', 3) == 'ft6'
    assert unit_power('s', 's') == 's^s'
    assert unit_power('m', 's') == 'm^s'
    assert unit_power('m2', 'm') == 'm^2m'
    assert unit_power('m2', 'm2') == 'm^4m'

# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:27:57 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
from unyts._helpers._multisplit import multisplit

def test_multisplit():
    assert multisplit('m2') == ('m2',)
    assert multisplit('km/h') == ('km','/','h')
    assert multisplit('mD*ft') == ('mD', '*', 'ft')
    assert multisplit('m/s2') == ('m','/','s2')
    assert multisplit('stb/day/psia') == ('stb', '/', 'day', '/', 'psia')

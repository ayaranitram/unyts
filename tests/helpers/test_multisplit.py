# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:27:57 2021

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.helpers.multi_split import multi_split

def test_multisplit():
    assert multi_split('m2') == ['m2']
    assert multi_split('km/h') == ['km', '/', 'h']
    assert multi_split('mD*ft') == ['mD', '*', 'ft']
    assert multi_split('m/s2') == ['m', '/', 's2']
    assert multi_split('stb/day/psia') == ['stb', '/', 'day', '/', 'psia']

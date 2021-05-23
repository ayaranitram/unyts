# -*- coding: utf-8 -*-
"""
Created on Sun May 23 09:56:26 2021

@author: martin
"""

from units._operations import unitBasePower

def test_unitBasePower():
    assert unitBasePower('m') == 'm'
    assert unitBasePower('ft') == 'ft'
    assert unitBasePower('m2') == 'm'
    assert unitBasePower('ft3') == 'ft'
    assert unitBasePower('1/m') == 'm'
    assert unitBasePower('1/ft') == 'ft'
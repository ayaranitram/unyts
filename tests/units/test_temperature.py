# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:23:13 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.temperature import temperature, temperatureGradient

t = temperature(35, 'C')
assert type(t) is temperature
assert t.name == 'temperature'
assert t.kind is temperature
assert t.value == 35
assert t.unit == 'C'

t = temperatureGradient(0.01, 'F/ft')
assert type(t) is temperatureGradient
assert t.name == 'temperatureGradient'
assert t.kind is temperatureGradient
assert t.value == 0.01
assert t.unit == 'F/ft'
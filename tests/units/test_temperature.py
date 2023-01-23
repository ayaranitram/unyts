# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:23:13 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.temperature import Temperature, TemperatureGradient

t = Temperature(35, 'C')
assert type(t) is Temperature
assert t.name == 'temperature'
assert t.kind is Temperature
assert t.value == 35
assert t.unit == 'C'

t = TemperatureGradient(0.01, 'F/ft')
assert type(t) is TemperatureGradient
assert t.name == 'temperature_gradient'
assert t.kind is TemperatureGradient
assert t.value == 0.01
assert t.unit == 'F/ft'

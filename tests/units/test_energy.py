# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 13:51:35 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.energy import Energy, Power, Current, Voltage
#from unyts.units.time import Time

e = Energy(100, 'Wh')
assert type(e) is Energy
assert e.name == 'energy'
assert e.kind is Energy
assert e.value == 100
assert e.unit == 'Wh'

p = Power(100, 'W')
assert type(p) is Power
assert p.name == 'power'
assert p.kind is Power
assert p.value == 100
assert p.unit == 'W'

i = Current(1.5, 'A')
assert type(i) is Current
assert i.name == 'current'
assert i.kind is Current
assert i.value == 1.5
assert i.unit == 'A'

v = Voltage(220, 'V')
assert type(v) is Voltage
assert v.name == 'voltage'
assert v.kind is Voltage
assert v.value == 220
assert v.unit == 'V'

#assert type(v * i) is Power
#assert type(p / i) is Voltage
#assert type(p / v) is Current
#t = Time(1, 'h')
#assert type(p * t) is Energy
#assert type(e / t) is Power
#assert type(e / p) is Time

# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:14:12 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.time import time
from unyts import units

t = time(60, 's')

assert type(t) is time
assert t.name == 'time'
assert t.kind is time
assert t.value == 60
assert t.unit == 's'

for op in ('+', '-', '*', '/'):
    print(t, op, 30)
    assert eval('t ' + op + ' 30') == units(eval('t.value ' + op + ' 30'), t.unit)

assert t * 3 == units(t.value * 3, t.unit)
assert t / 3 == units(t.value / 3, t.unit)
assert t ** 3 == units(t.value ** 3, t.unit + str(3))

for op in ('+', '-'):
    print(30, op, t)
    assert eval('30 ' + op + ' t') == units(eval('30 ' + op + ' t.value'), t.unit)

assert 3 * t == units(t.value * 3, t.unit)
assert 3 / t == units(3 / t.value, t.unit + '-1')
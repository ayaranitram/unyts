# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:28:23 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.unitless import dimensionless, percentage
from unyts.dictionaries import dictionary
from unyts import units, convert


for p in dictionary['percentage']:
    for d in dictionary['dimensionless']:
        print(p, 'to', d)
        assert convert(75.0, p, d) == 0.75
        print(d, 'to', p)
        assert convert(0.50, d, p) == 50.0
    for q in dictionary['percentage']:
        print(p, 'to', q)
        assert convert(25.0, p, q) == 25.0
for d in dictionary['dimensionless']:
    for b in dictionary['dimensionless']:
        print(d, 'to', b)
        assert convert(0.33, d, b) == 0.33




p = percentage(50, '%')
assert type(p) is percentage
assert p.name == 'percentage'
assert p.kind is percentage
assert p.value == 0.5
assert p.unit == '%'

f = dimensionless(0.25, 'fraction')
assert type(f) is dimensionless
assert f.name == 'dimensionless'
assert f.kind is dimensionless
assert f.value == 0.25
assert f.unit == 'fraction'

d = dimensionless(0.3)
assert type(d) is dimensionless
assert d.name == 'dimensionless'
assert d.kind is dimensionless
assert d.value == 0.3
assert d.unit == 'dimensionless'

for op in ('+', '-', '*', '/', '**', '%'):
    print(p, op, f)
    assert eval('p ' + op + ' f') == units(eval('p.value ' + op + ' f.value') * 100, p.unit)

for op in ('+', '-', '*', '/', '**', '%'):
    print(p, op, 3.0)
    assert eval('p ' + op + ' 3.0') == units(eval('p.value ' + op + ' 3.0') * 100, p.unit)

for op in ('+', '-', '*', '/'):
    print(3.0, op, p)
    assert eval('3.0 ' + op + ' p') == units(eval('3.0 ' + op + ' p.value') * 100, p.unit)

for op in ('+', '-', '*', '/', '**', '%'):
    print(f, op, p)
    assert eval('f ' + op + ' p') == units(eval('f.value ' + op + ' p.value'), f.unit)

for op in ('+', '-', '*', '/'):
    print(p, op, 3.0)
    assert eval('f ' + op + ' 3.0') == units(eval('f.value ' + op + ' 3.0'), f.unit)
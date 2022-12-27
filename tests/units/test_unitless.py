# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:28:23 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.unitless import Dimensionless, Percentage
from unyts.dictionaries import dictionary
from unyts import units, convert

for p in dictionary['Percentage']:
    for d in dictionary['Dimensionless']:
        print(p, 'to', d)
        assert convert(75.0, p, d) == 0.75
        print(d, 'to', p)
        assert convert(0.50, d, p) == 50.0
    for q in dictionary['Percentage']:
        print(p, 'to', q)
        assert convert(25.0, p, q) == 25.0
for d in dictionary['Dimensionless']:
    for b in dictionary['Dimensionless']:
        print(d, 'to', b)
        assert convert(0.33, d, b) == 0.33

p = Percentage(50, '%')
assert type(p) is Percentage
assert p.name == 'Percentage'
assert p.kind is Percentage
assert p.value == 0.5
assert p.unit == '%'

f = Dimensionless(0.25, 'fraction')
assert type(f) is Dimensionless
assert f.name == 'Dimensionless'
assert f.kind is Dimensionless
assert f.value == 0.25
assert f.unit == 'fraction'

d = Dimensionless(0.3)
assert type(d) is Dimensionless
assert d.name == 'Dimensionless'
assert d.kind is Dimensionless
assert d.value == 0.3
assert d.unit == 'Dimensionless'

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

# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 11:59:21 2023

@author: martin
"""

from unyts.units.force import Pressure, Weight, Compressibility, Viscosity
from unyts.errors import WrongUnitsError

p = Pressure(2.4, 'barsa')
assert type(p) is Pressure
assert p.name == 'pressure'
assert p.kind is Pressure
assert p.value == 2.4
assert p.unit == 'barsa'

w = Weight(1, 'kg')
assert type(w) is Weight
assert w.name == 'weight'
assert w.kind is Weight
assert w.value == 1
assert w.unit == 'kg'

oz = Weight(1, 'ounce')
assert type(oz) is Weight
assert oz.name == 'weight'
assert oz.kind is Weight
assert oz.value == 1
assert oz.unit == 'ounce'


assert oz.to('g') == Weight(28.349523125, 'g')
try:
    oz.to('l')
except WrongUnitsError:
    pass

c = Compressibility(3e-6, '1/psi')
assert type(c) is Compressibility
assert c.name == 'compressibility'
assert c.kind is Compressibility
assert c.value == 3e-6
assert c.unit == '1/psi'

v = Viscosity(1, 'cP')
assert type(v) is Viscosity
assert v.name == 'viscosity'
assert v.kind is Viscosity
assert v.value == 1
assert v.unit == 'cP'

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 13:51:35 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.units.energy import Energy, Power, Current, Voltage, Conductance, \
    Capacitance, Resistance, Charge
from unyts.units.time import Time

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

s = Conductance(1, 'Siemen')
assert type(s) is Conductance
assert s.name == 'conductance'
assert s.kind is Conductance
assert s.value == 1
assert s.unit == 'Siemen'

f = Capacitance(1, 'Farad')
assert type(f) is Capacitance
assert f.name == 'capacitance'
assert f.kind is Capacitance
assert f.value == 1
assert f.unit == 'Farad'

r = Resistance(12, 'ohm')
assert type(r) is Resistance
assert r.name == 'resistance'
assert r.kind is Resistance
assert r.value == 12
assert r.unit == 'ohm'

c = Charge(1, 'Coulomb')
assert type(c) is Charge
assert c.name == 'charge'
assert c.kind is Charge
assert c.value == 1
assert c.unit == 'Coulomb'

t = Time(1, 'h')

assert type(e / t) is Power
assert (e / t).unit == 'Watt'

assert type(p * t) is Energy
assert (p * t).unit == 'Wh'

assert type(e / p) is Time
assert (e / p).unit == 'hour'

assert type(p / i) is Voltage
assert (p / i).unit == 'Volt'

assert type(p / v) is Current
assert (p / v).unit == 'Ampere'

assert type(i * r) is Voltage
assert (i * r).unit == 'Volt'

assert type(v * i) is Power
assert (v * i).units == 'Watt'

assert type(v * f) is Charge
assert (v * f).units == 'Coulomb'

assert type(v / i) is Resistance
assert (v / i).units == 'Ohm'

assert type(v / r) is Current
assert (v / r).units == 'Ampere'

assert type(r * i) is Voltage
assert (r * i).unit == 'Volt'

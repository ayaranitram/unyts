#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.12'
__release__ = 20230121
__all__ = ['Energy', 'Power', 'Current', 'Voltage', 'Resistance', 'Conductance', 'Capacitance', 'Charge', 'Inductance', 'Impedance']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric
from .time import Time


class Energy(Unit):
    classUnits = _dictionary['Energy']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'energy'
        self.kind = Energy
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __truediv__(self, other):
        if type(other) is Time:
            return super().__truediv__(other).to('Watt')
        if type(other) is Power:
            return super().__truediv__(other).to('hour')
        else:
            return super().__truediv__(other)


class Power(Unit):
    classUnits = _dictionary['Power']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'power'
        self.kind = Power
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __mul__(self, other):
        if type(other) is Time:
            return super().__mul__(other).to('Wh')
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        if type(other) is Current:
            return super().__truediv__(other).to('Volt')
        elif type(other) is Voltage:
            return super().__truediv__(other).to('Ampere')
        else:
            return super().__truediv__(other)


class Current(Unit):
    classUnits = _dictionary['Current']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'current'
        self.kind = Current
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __mul__(self, other):
        if type(other) is Resistance:
            return super().__mul__(other).to('Volt')
        else:
            return super().__mul__(other)


class Voltage(Unit):
    classUnits = _dictionary['Voltage']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'voltage'
        self.kind = Voltage
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __mul__(self, other):
        if type(other) is Current:
            return super().__mul__(other).to('Watt')
        if type(other) is Capacitance:
            return super().__mul__(other).to('Coulomb')
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        if type(other) is Current:
            return super().__truediv__(other).to('Ohm')
        elif type(other) is Resistance:
            return super().__truediv__(other).to('Ampere')
        else:
            return super().__truediv__(other)


class Resistance(Unit):
    classUnits = _dictionary['Resistance']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'resistance'
        self.kind = Resistance
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __mul__(self, other):
        if type(other) is Current:
            return super().__mul__(other).to('Volt')
        else:
            return super().__mul__(other)


class Conductance(Unit):
    classUnits = _dictionary['Conductance']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'conductance'
        self.kind = Conductance
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Capacitance(Unit):
    classUnits = _dictionary['Capacitance']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'capacitance'
        self.kind = Capacitance
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __mul__(self, other):
        if type(other) is Voltage:
            return super().__mul__(other).to('Coulomb')
        else:
            return super().__mul__(other)


class Charge(Unit):
    classUnits = _dictionary['Charge']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'charge'
        self.kind = Charge
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

    def __truediv__(self, other):
        if type(other) is Voltage:
            return super().__truediv__(other).to('Farad')
        else:
            return super().__truediv__(other)


class Inductance(Unit):
    classUnits = _dictionary['Inductance']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'inductance'
        self.kind = Inductance
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Impedance(Unit):
    classUnits = _dictionary['Impedance']

    def __init__(self, value: numeric, unit: unit_or_str):
        self.name = 'Impedance'
        self.kind = Impedance
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

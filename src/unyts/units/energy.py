#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.31'
__release__ = 20250323
__all__ = ['Energy', 'Power', 'Current', 'Voltage', 'Resistance', 'Conductance', 'Capacitance', 'Charge', 'Inductance', 'Impedance']

from ..dictionaries import dictionary as _dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric
from .time import Time


class Energy(Unit):
    class_units = _dictionary['Energy']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'energy' if name is None else name
        super().__init__(value, units, name)
        self.kind = Energy
        self.__unit = self.check_unit(units)

    def __truediv__(self, other):
        if type(other) is Time:
            return super().__truediv__(other).to('Watt')
        if type(other) is Power:
            return super().__truediv__(other).to('hour')
        else:
            return super().__truediv__(other)


class Power(Unit):
    class_units = _dictionary['Power']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'power' if name is None else name
        super().__init__(value, units, name)
        self.kind = Power
        self.__unit = self.check_unit(units)

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
    class_units = _dictionary['Current']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'current' if name is None else name
        super().__init__(value, units, name)
        self.kind = Current
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        if type(other) is Resistance:
            return super().__mul__(other).to('Volt')
        else:
            return super().__mul__(other)


class Voltage(Unit):
    class_units = _dictionary['Voltage']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'voltage' if name is None else name
        super().__init__(value, units, name)
        self.kind = Voltage
        self.__unit = self.check_unit(units)

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
    class_units = _dictionary['Resistance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'resistance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Resistance
        self.__value = self.check_value(value)
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        if type(other) is Current:
            return super().__mul__(other).to('Volt')
        else:
            return super().__mul__(other)


class Conductance(Unit):
    class_units = _dictionary['Conductance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'conductance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Conductance
        self.__unit = self.check_unit(units)


class Capacitance(Unit):
    class_units = _dictionary['Capacitance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'capacitance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Capacitance
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        if type(other) is Voltage:
            return super().__mul__(other).to('Coulomb')
        else:
            return super().__mul__(other)


class Charge(Unit):
    class_units = _dictionary['Charge']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'charge' if name is None else name
        super().__init__(value, units, name)
        self.kind = Charge
        self.__unit = self.check_unit(units)

    def __truediv__(self, other):
        if type(other) is Voltage:
            return super().__truediv__(other).to('Farad')
        else:
            return super().__truediv__(other)


class Inductance(Unit):
    class_units = _dictionary['Inductance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'inductance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Inductance
        self.__unit = self.check_unit(units)


class Impedance(Unit):
    class_units = _dictionary['Impedance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        name = 'Impedance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Impedance
        self.__unit = self.check_unit(units)

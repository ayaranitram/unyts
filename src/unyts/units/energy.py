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
    """A class to represent energy quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Energy']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize an Energy object with a value and units."""
        name = 'energy' if name is None else name
        super().__init__(value, units, name)
        self.kind = Energy
        self.__unit = self.check_unit(units)

    def __truediv__(self, other):
        """Divide an Energy object by a Time or Power object."""
        if type(other) is Time:
            return super().__truediv__(other).to('Watt')
        if type(other) is Power:
            return super().__truediv__(other).to('hour')
        else:
            return super().__truediv__(other)


class Power(Unit):
    """A class to represent power quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Power']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Power object with a value and units."""
        name = 'power' if name is None else name
        super().__init__(value, units, name)
        self.kind = Power
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        """Multiply a Power object by a Time object to get Energy."""
        if type(other) is Time:
            return super().__mul__(other).to('Wh')
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        """Divide a Power object by a Time object to get Energy, or by a Current or Resistance to get Voltage."""
        if type(other) is Current:
            return super().__truediv__(other).to('Volt')
        elif type(other) is Voltage:
            return super().__truediv__(other).to('Ampere')
        else:
            return super().__truediv__(other)


class Current(Unit):
    """A class to represent current quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Current']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Current object with a value and units."""
        name = 'current' if name is None else name
        super().__init__(value, units, name)
        self.kind = Current
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        """Multiply a Current object by a Voltage object to get Power, or by a Resistance object to get Voltage."""
        if type(other) is Resistance:
            return super().__mul__(other).to('Volt')
        else:
            return super().__mul__(other)


class Voltage(Unit):
    """A class to represent voltage quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Voltage']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Voltage object with a value and units."""
        name = 'voltage' if name is None else name
        super().__init__(value, units, name)
        self.kind = Voltage
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        """Multiply a Voltage object by a Current object to get Power, or by a Capacitance object to get Charge."""
        if type(other) is Current:
            return super().__mul__(other).to('Watt')
        if type(other) is Capacitance:
            return super().__mul__(other).to('Coulomb')
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        """Divide a Voltage object by a Current object to get Resistance, or by a Resistance object to get Current."""
        if type(other) is Current:
            return super().__truediv__(other).to('Ohm')
        elif type(other) is Resistance:
            return super().__truediv__(other).to('Ampere')
        else:
            return super().__truediv__(other)


class Resistance(Unit):
    """A class to represent resistance quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Resistance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Resistance object with a value and units."""
        name = 'resistance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Resistance
        self.__value = self.check_value(value)
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        """Multiply a Resistance object by a Current object to get Voltage."""
        if type(other) is Current:
            return super().__mul__(other).to('Volt')
        else:
            return super().__mul__(other)


class Conductance(Unit):
    """A class to represent conductance quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Conductance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Conductance object with a value and units."""
        name = 'conductance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Conductance
        self.__unit = self.check_unit(units)


class Capacitance(Unit):
    """A class to represent capacitance quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Capacitance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Capacitance object with a value and units."""
        name = 'capacitance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Capacitance
        self.__unit = self.check_unit(units)

    def __mul__(self, other):
        """Multiply a Capacitance object by a Voltage object to get Charge."""
        if type(other) is Voltage:
            return super().__mul__(other).to('Coulomb')
        else:
            return super().__mul__(other)


class Charge(Unit):
    """A class to represent charge quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Charge']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize a Charge object with a value and units."""
        name = 'charge' if name is None else name
        super().__init__(value, units, name)
        self.kind = Charge
        self.__unit = self.check_unit(units)

    def __truediv__(self, other):
        """Divide a Charge object by a Voltage object to get Capacitance."""
        if type(other) is Voltage:
            return super().__truediv__(other).to('Farad')
        else:
            return super().__truediv__(other)


class Inductance(Unit):
    """A class to represent inductance quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Inductance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize an Inductance object with a value and units."""
        name = 'inductance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Inductance
        self.__unit = self.check_unit(units)


class Impedance(Unit):
    """A class to represent impedance quantities with associated units, supporting arithmetic operations and unit conversions."""
    class_units = _dictionary['Impedance']
    __slots__ = ('__unit', '__value', 'name', 'kind')

    def __init__(self, value: numeric, units: unit_or_str, name=None):
        """Initialize an Impedance object with a value and units."""
        name = 'Impedance' if name is None else name
        super().__init__(value, units, name)
        self.kind = Impedance
        self.__unit = self.check_unit(units)

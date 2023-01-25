#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.12'
__release__ = 20230124
__all__ = ['Unit', 'is_Unit']

from .errors import WrongUnitsError, WrongValueError, NoConversionFoundError
from .operations import unit_product as _unit_product, unit_division as _unit_division, \
    unit_base_power as _unit_base_power
from .helpers.unit_string_tools import reduce_units as _reduce_units
from .converter import convert as _convert, convertible as _convertible
from numbers import Number


try:
    import numpy as np
    from numpy import ndarray, int64, float64, int32, float32
    _numpy_ = True
except ModuleNotFoundError:
    _numpy_ = False
try:
    from pandas import Series, DataFrame
    _pandas_ = True
except ModuleNotFoundError:
    _pandas_ = False

if _numpy_ and _pandas_:
    number = (int, float, complex, int32, int64, float32, float64)
    numeric = (int, float, complex, int32, int64, float32, float64, ndarray, Series, DataFrame)
    array_like = (ndarray, Series, DataFrame)
elif _numpy_:
    number = (int, float, complex, int32, int64, float32, float64)
    numeric = (int, float, complex, ndarray, int32, int64, float32, float64)
    array_like = (ndarray,)
elif _pandas_:
    number = (int, float, complex)
    numeric = (int, float, complex, Series, DataFrame)
    array_like = (Series, DataFrame)
else:
    number = (int, float, complex)
    numeric = (int, float, complex)
    array_like = tuple()


class UnytType(type):
    def __repr__(self):
        return self.__name__


class Unit(object, metaclass=UnytType):
    """
    A class to cope with values associated to units, its arithmetic and logic
    operations and conversions.
    """

    def __init__(self, value=None, unit=None):
        self.unit = None
        self.value = None
        self.name = None
        self.kind = None
        if value is not None and unit is not None:
            from .units.define import units
            u = units(value, unit)
            self.unit = u.unit
            self.value = u.value
            self.name = u.name
            self.kind = u.kind

    def __call__(self) -> numeric:
        return self.value

    def __repr__(self) -> str:
        return str(self.value) + '_' + str(self.unit)

    def __str__(self) -> str:
        return str(self.value) + '_' + str(self.unit)

    @property
    def dtype(self):
        if hasattr(self.values, 'dtype'):
            return self.values.dtype
        elif _numpy_:
            if type(self.value) is int:
                return np.dtype(int)
            elif type(self.value) is float:
                return np.dtype(float)
            elif type(self.value) is complex:
                return np.dtype(complex)
        else:
            raise NotImplementedError("dtype not implemented without NumPy.")

    def convert(self, new_unit: str):
        if type(new_unit) is not str and hasattr(new_unit, 'units') and type(new_unit.units) is str:
            new_unit = new_unit.units
        elif type(new_unit) is not str:
            raise TypeError("`new_units` should be string.")
        if not _convertible(self.unit, new_unit):
            raise WrongUnitsError("'" + str(new_unit) + "' is not valid units for '" + str(self.name) + "'.")
        return self.kind(_convert(self.value, self.unit, new_unit), new_unit)

    def to(self, new_unit):
        return self.convert(new_unit)

    def __neg__(self):
        return self.kind(self.value.__neg__(), self.unit)

    def __bool__(self):
        from .units.custom import UserUnits
        from .units.unitless import Dimensionless, Percentage
        if self.kind in (Dimensionless, Percentage, UserUnits):
            return False
        return True

    def __abs__(self):
        return self.kind(abs(self.value), self.unit)

    def __add__(self, other):
        from .units.unitless import Dimensionless, Percentage
        if isinstance(other, Unit):
            if other.kind is self.kind:
                if self.unit == other.unit:
                    return self.kind(self.value + other.value, self.unit)
                elif _convertible(other.unit, self.unit):
                    return self.kind(self.value + _convert(other.value, other.unit, self.unit), self.unit)
                elif _convertible(self.unit, other.unit):
                    return self.kind(other.value + _convert(self.value, self.unit, other.unit), other.unit)
                else:
                    raise NoConversionFoundError("from '" + self.unit + "' to '" + other.unit + "'")
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return self.kind(self.value + other.value, other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value + other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value + other.value, self.unit)
            else:  # add different units
                return self, other
        elif type(other) is tuple:
            result, flag = [], False
            for each in other:
                if type(each) is type(self):
                    result += [self + each]
                    flag = True
                else:
                    result += each
            return tuple(result) if flag else other + (self,)
        elif self.kind is Percentage:
            return self.kind((self.value + other) * 100, self.unit)
        elif type(other) in numeric:
            return self.kind(self.value + other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__radd__(self)
        else:
            raise NotImplementedError("Addition of " + str(type(self)) + " and " + str(type(other)) + " not implemented.")

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if isinstance(other, Unit):
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return other.kind(self.value * other.value, other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value * other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value * other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value * other.value, _unit_product(self.unit, other.unit))
            elif _convertible(other.unit, self.unit):
                return units(self.value * _convert(other.value, other.unit, self.unit),
                             _unit_product(self.unit, other.unit))
            elif _convertible(self.unit, other.unit):
                return units(other.value * _convert(self.value, self.unit, other.unit),
                             _unit_product(other.unit, self.unit))
            elif _convertible(_unit_base_power(self.unit)[0], _unit_base_power(other.unit)[0]):
                factor = _convert(1, _unit_base_power(other.unit)[0], _unit_base_power(self.unit)[0])
                return units(self.value * other.value * factor, _unit_product(self.unit, other.unit))
            else:
                return units(self.value * other.value, _unit_product(self.unit, other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self * each]
            return tuple(result)
        elif self.kind is Percentage:
            return self.kind(self.value * other * 100, self.unit)
        elif type(other) in numeric:
            return self.kind(self.value * other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rmul__(self)
        else:
            raise NotImplementedError("Product of " + str(type(self)) + " and " + str(type(other)) + " not implemented.")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if isinstance(other, Unit):
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return other.kind(self.value ** other.value, other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value ** other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value ** other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value ** other.value, self.unit + '^' + other.unit)
            elif _convertible(other.unit, self.unit):
                return units(self.value ** _convert(other.value, other.unit, self.unit), self.unit + '^' + self.unit)
            elif _convertible(_unit_base_power(self.unit)[0], _unit_base_power(other.unit)[0]):
                factor = _convert(1, _unit_base_power(other.unit)[0], _unit_base_power(self.unit)[0])
                return units(self.value ** (other.value * factor), self.unit + '^' + other.unit)
            else:
                return units(self.value ** other.value, self.unit + '^' + other.unit)
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self ** each]
            return tuple(result)
        elif self.kind is Percentage:
            return self.kind((self.value ** other) * 100, self.unit)
        elif type(other) in numeric:
            pow_units = _unit_base_power(self.unit)[1] * other
            if pow_units == 0:
                pow_units = 'Dimensionless'
            elif pow_units == 1:
                pow_units = _unit_base_power(self.unit)[0]
            else:
                pow_units = _unit_base_power(self.unit)[0] + str(pow_units)
            return units(self.value ** other, pow_units)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rpow__(self)
        else:
            raise NotImplementedError("Power of " + str(type(self)) + " to " + str(type(other)) + " not implemented.")

    def __rpow__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if self.kind is Percentage:
            return units((other ** self.value), 'Dimensionless')
        elif self.kind is Dimensionless:
            return units(other ** self.value, self.unit)
        else:
            raise TypeError("unsupported operand type(s) for ** or pow(): '" + str(type(other)) + "' and '" + self.name)

    def __sub__(self, other):
        # return self.__add__(other * -1)
        from .units.unitless import Dimensionless, Percentage
        if isinstance(other, Unit):
            if other.kind is self.kind:
                if self.unit == other.unit:
                    return self.kind(self.value - other.value, self.unit)
                elif _convertible(other.unit, self.unit):
                    return self.kind(self.value - _convert(other.value, other.unit, self.unit), self.unit)
                elif _convertible(self.unit, other.unit):
                    return self.kind(other.value - _convert(self.value, self.unit, other.unit), other.unit)
                else:
                    raise NoConversionFoundError("from '" + self.unit + "' to '" + other.unit + "'")
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return self.kind(self.value - other.value, other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value - other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value - other.value, self.unit)
            else:  # add different units
                return self, other
        elif type(other) is tuple:
            result, flag = [], False
            for each in other:
                if type(each) is type(self):
                    result += [self - each]
                    flag = True
                else:
                    result += each
            return tuple(result) if flag else other + (self,)
        elif self.kind is Percentage:
            return self.kind((self.value - other) * 100, self.unit)
        elif type(other) in numeric:
            return self.kind(self.value - other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rsub__(self)
        else:
            raise NotImplementedError("Subtraction of " + str(type(self)) + " and " + str(type(other)) + " not implemented.")

    def __rsub__(self, other):
        return self.__neg__() + other

    def __truediv__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if isinstance(other, Unit):
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return other.kind(self.value / other.value, '1/' + other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value / other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value / other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value / other.value, _unit_division(self.unit, other.unit))
            elif _convertible(other.unit, self.unit):
                return units(self.value / _convert(other.value, other.unit, self.unit),
                             _unit_division(self.unit, other.unit))
            elif _convertible(_unit_base_power(self.unit)[0], _unit_base_power(other.unit)[0]):
                factor = _convert(1, _unit_base_power(other.unit)[0], _unit_base_power(self.unit)[0])
                return units(self.value / (other.value * factor), _unit_division(self.unit, other.unit))
            else:
                return units(self.value / other.value, _unit_division(self.unit, other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self / each]
            return tuple(result)
        elif self.kind is Percentage:
            return self.kind(self.value / other * 100, self.unit)
        elif type(other) in numeric:
            return units(self.value / other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rtruediv__(self)
        else:
            raise NotImplementedError("Division of " + str(type(self)) + " by " + str(type(other)) + " not implemented.")

    def __rtruediv__(self, other):
        from .units.define import units
        from .units.unitless import Dimensionless, Percentage
        if self.kind is Percentage:
            return units(other / self.value * 100, self.unit)
        elif self.kind is Dimensionless:
            return units(other / self.value, self.unit)
        elif type(other) in numeric:
            return units(other / self.value, self.unit + '-1')
        else:
            raise NotImplementedError("Division of " + str(type(self)) + " by " + str(type(other)) + " not implemented.")

    def __floordiv__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if isinstance(other, Unit):
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return other.kind(self.value // other.value, '1/' + other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value // other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value // other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value // other.value, _unit_division(self.unit, other.unit))
            elif _convertible(other.unit, self.unit):
                return units(self.value // _convert(other.value, other.unit, self.unit),
                             _unit_division(self.unit, other.unit))
            elif _convertible(_unit_base_power(self.unit)[0], _unit_base_power(other.unit)[0]):
                factor = _convert(1, _unit_base_power(other.unit)[0], _unit_base_power(self.unit)[0])
                return units(self.value // (other.value * factor), _unit_division(self.unit, other.unit))
            else:
                return units(self.value // other.value, _unit_division(self.unit, other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self // each]
            return tuple(result)
        elif self.kind is Percentage:
            return self.kind(self.value // other * 100, self.unit)
        elif type(other) in numeric:
            return self.kind(self.value // other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rfloordiv__(self)
        else:
            raise NotImplementedError("Division of " + str(type(self)) + " by " + str(type(other)) + " not implemented.")

    def __rfloordiv__(self, other):
        from .units.define import units
        from .units.unitless import Dimensionless, Percentage
        if self.kind is Percentage:
            return units(other // self.value * 100, self.unit)
        elif self.kind is Dimensionless:
            return units(other // self.value, self.unit)
        elif type(other) in numeric:
            return units(other // self.value, self.unit + '-1')
        else:
            raise NotImplementedError("Division of " + str(type(self)) + " by " + str(type(other)) + " not implemented.")

    def __matmul__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if isinstance(other, Unit):
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return other.kind(self.value / other.value, '1/' + other.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value / other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value / other.value, self.unit)
            else:
                return units(self.value / other.value, _reduce_units(self.unit + '/' + other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self / each]
            return tuple(result)
        elif self.kind is Percentage:
            return self.kind(self.value / other * 100, self.unit)
        elif type(other) in numeric:
            return self.kind(self.value / other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rmatmul__(self)
        else:
            raise NotImplementedError("Division of " + str(type(self)) + " by " + str(type(other)) + " not implemented.")

    def __mod__(self, other):
        from .units.unitless import Dimensionless, Percentage
        from .units.define import units
        if isinstance(other, Unit):
            if self.kind in (Dimensionless, Percentage) and other.kind not in (Dimensionless, Percentage):
                return other.kind(self.value % other.value, self.unit)
            elif self.kind is Percentage and other.kind in (Dimensionless, Percentage):
                return self.kind((self.value % other.value) * 100, self.unit)
            elif other.kind in (Dimensionless, Percentage):
                return self.kind(self.value % other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value % other.value, self.unit)
            elif _convertible(other.unit, self.unit):
                return units(self.value % _convert(other.value, other.unit, self.unit), self.unit)
            elif _convertible(_unit_base_power(self.unit)[0], _unit_base_power(other.unit)[0]):
                factor = _convert(1, _unit_base_power(other.unit)[0], _unit_base_power(self.unit)[0])
                return units(self.value % (other.value * factor), self.unit)
            else:
                return units(self.value % other.value, self.unit)
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self % each]
            return tuple(result)
        elif self.kind is Percentage:
            return self.kind(self.value % other * 100, self.unit)
        elif type(other) in numeric:
            return self.kind(self.value % other, self.unit)
        elif hasattr(other, 'type') and other.type in ('SimSeries', 'SimDataFrame'):
            return other.__rmod__(self)
        else:
            raise NotImplementedError("Module of " + str(type(self)) + " when divided by " + str(type(other)) + " not implemented.")

    def __lt__(self, other) -> bool:
        if type(self) == type(other):
            return self.value < other.convert(self.unit).value
        else:
            msg = "'<' not supported between instances of '" + \
                  (str(type(self))[
                   str(type(self)).index("'") + 1:len(str(type(self))) - str(type(self))[::-1].index("'") - 1]).replace(
                      '__main__.', '') + \
                  "' and '" + \
                  (str(type(other))[
                   str(type(other)).index("'") + 1:len(str(type(other))) - str(type(other))[::-1].index(
                       "'") - 1]).replace('__main__.', '') + "'"
            raise TypeError(msg)

    def __le__(self, other) -> bool:
        if type(self) == type(other):
            return self.value <= other.convert(self.unit).value
        else:
            msg = "'<=' not supported between instances of '" + \
                  (str(type(self))[
                   str(type(self)).index("'") + 1:len(str(type(self))) - str(type(self))[::-1].index("'") - 1]).replace(
                      '__main__.', '') + \
                  "' and '" + \
                  (str(type(other))[
                   str(type(other)).index("'") + 1:len(str(type(other))) - str(type(other))[::-1].index(
                       "'") - 1]).replace('__main__.', '') + "'"
            raise TypeError(msg)

    def __eq__(self, other) -> bool:
        if type(self) is type(other):
            return self.value == other.convert(self.unit).value
        else:
            msg = "'==' not supported between instances of '" + \
                  (str(type(self))[
                   str(type(self)).index("'") + 1:len(str(type(self))) - str(type(self))[::-1].index("'") - 1]).replace(
                      '__main__.', '') + \
                  "' and '" + \
                  (str(type(other))[
                   str(type(other)).index("'") + 1:len(str(type(other))) - str(type(other))[::-1].index(
                       "'") - 1]).replace('__main__.', '') + "'"
            raise TypeError(msg)

    def __ne__(self, other):
        if type(self) is type(other):
            return self.value != other.convert(self.unit).value
        else:
            msg = "'!=' not supported between instances of '" + \
                  (str(type(self))[
                   str(type(self)).index("'") + 1:len(str(type(self))) - str(type(self))[::-1].index("'") - 1]).replace(
                      '__main__.', '') + \
                  "' and '" + \
                  (str(type(other))[
                   str(type(other)).index("'") + 1:len(str(type(other))) - str(type(other))[::-1].index(
                       "'") - 1]).replace('__main__.', '') + "'"
            raise TypeError(msg)

    def __ge__(self, other):
        if type(self) is type(other):
            return self.value >= other.convert(self.unit).value
        else:
            msg = "'>=' not supported between instances of '" + \
                  (str(type(self))[
                   str(type(self)).index("'") + 1:len(str(type(self))) - str(type(self))[::-1].index("'") - 1]).replace(
                      '__main__.', '') + \
                  "' and '" + \
                  (str(type(other))[
                   str(type(other)).index("'") + 1:len(str(type(other))) - str(type(other))[::-1].index(
                       "'") - 1]).replace('__main__.', '') + "'"
            raise TypeError(msg)

    def __gt__(self, other):
        if type(self) is type(other):
            return self.value > other.convert(self.unit).value
        else:
            msg = "'>' not supported between instances of '" + \
                  (str(type(self))[
                   str(type(self)).index("'") + 1:len(str(type(self))) - str(type(self))[::-1].index("'") - 1]).replace(
                      '__main__.', '') + \
                  "' and '" + \
                  (str(type(other))[
                   str(type(other)).index("'") + 1:len(str(type(other))) - str(type(other))[::-1].index(
                       "'") - 1]).replace('__main__.', '') + "'"
            raise TypeError(msg)

    def __len__(self):
        try:
            return len(self.value)
        except TypeError:
            return 1

    def __round__(self, n=None):
        return self.kind(round(self.value, n), self.unit)

    def __getitem__(self, item):
        if type(item) is int:
            if item >= len(self):
                raise IndexError
        else:
            raise ValueError
        from .units.unitless import Percentage
        if self.kind is Percentage:
            return self.kind(self.value[item] * 100, self.unit)
        else:
            return self.kind(self.value[item], self.unit)

    def __iter__(self):
        if type(self.value) in (int, float):
            return np.array((self.value,)).__iter__()
        else:
            return self.value.__iter__()

    def get_unit(self):
        return self.unit

    def get_units(self):
        return self.get_unit()

    @property
    def units(self):
        return self.unit

    def get_value(self):
        return self.value

    @property
    def values(self):
        return self.value

    def check_value(self, value):
        if type(value) in (list, tuple):
            try:
                return np.array(value)
            except TypeError:
                raise WrongValueError(str(value))
        elif isinstance(value, Number):
            return value
        elif isinstance(value, array_like):
            return value
        else:
            raise WrongValueError(str(value))

    def check_unit(self, units):
        if type(units) is str:
            pass
        elif type(units) is not str and hasattr(units, 'units'):
            units = units.unit
        else:
            raise WrongUnitsError("'" + str(units) + "' for '" + str(self.name) + "'")
        if units != 'ounce' and units in self.kind.classUnits:
            return units
        elif units == 'ounce':
            return units
        else:
            raise WrongUnitsError("'" + str(units) + "' for '" + str(self.name) + "'")


def is_Unit(obj) -> bool:
    return isinstance(obj, Unit)

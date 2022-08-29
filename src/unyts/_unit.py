#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.2.5'
__release__ = 20220830


import numpy as np
from pandas import Series, DataFrame
from ._errors import WrongUnits as _WrongUnits, WrongValue as _WrongValue
from ._operations import unitProduct, unitDivision, unitBasePower
from ._convert import converter as _converter, convertible as _convertible


class _units(object):
    """
    A class to cope with values associated to units, its arithmetic and logic
    operations and conversions.
    """

    def __init__(self):
        self.unit = None
        self.value = None
        self.name = None
        self.kind = None

    def __call__(self):
        return self.value

    def __repr__(self):
        return str(self.value) + '_' + str(self.unit)
    def __str__(self) :
        return str(self.value) + '_' + str(self.unit)

    def convert(self, newunit):
        if type(newunit) is not str:
            try:
                newunit = newunit.unit
            except:
                raise _WrongUnits()
        return self.kind(_converter(self.value, self.unit, newunit), newunit)

    def to(self, newunit):
        return self.convert(newunit)

    def __neg__(self):
        return self.kind(self.value * -1, self.unit)

    def __bool__(self):
        from .units.custom import userUnits
        from .units.unitless import dimensionless
        if self.kind in [dimensionless, userUnits]:
            return False
        return True

    def __abs__(self):
        return self.kind(abs(self.value), self.unit)

    def __add__(self, other):
        from .units.unitless import dimensionless
        if '.units.' in str(type(other)):
            if other.kind is self.kind:
                if self.unit == other.unit:
                    return self.kind(self.value + other.value, self.unit)
                else:
                    return self.kind(self.value + _converter(other.value, other.unit, self.unit), self.unit)
            if other.kind is dimensionless:
                return self.kind(self.value + other.value * self.value, self.unit)
            else : # add different units
                return (self, other)
        elif type(other) is tuple:
            result, flag = [], False
            for each in other:
                if type(each) is type(self):
                    result += [self + each]
                    flag = True
                else:
                    result += each
            return tuple(result) if flag else other + (self,)
        else:
            return self.kind(self.value + other, self.unit)
    def __radd__(self,other):
        return self.__add__(other)

    def __mul__(self,other):
        from .units.unitless import dimensionless
        from .units.define import units
        if '.units.' in str(type(other)):
            if self.kind is dimensionless:
                return other.kind(self.value * other.value, other.unit)
            elif other.kind is dimensionless:
                return self.kind(self.value * other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value * other.value, unitProduct(self.unit, other.unit))
            elif _convertible(other.unit, self.unit):
                return units(self.value * _converter(other.value, other.unit, self.unit), unitProduct(self.unit, other.unit))
            elif _convertible(unitBasePower(self.unit)[0], unitBasePower(other.unit)[0]):
                factor = _converter(1, unitBasePower(other.unit)[0], unitBasePower(self.unit)[0])
                return units(self.value * other.value * factor, unitProduct(self.unit,other.unit))
            else:
                return units(self.value * other.value,unitProduct(self.unit,other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self * each]
            return tuple(result)
        else:
            return self.kind(self.value * other,self.unit)

    def __rmul__(self,other):
        return self.__mul__(other)

    def __pow__(self,other):
        from .units.unitless import dimensionless
        from .units.define import units
        if '.units.' in str(type(other)):
            if self.kind is dimensionless:
                return other.kind(self.value ** other.value, other.unit)
            elif other.kind is dimensionless:
                return self.kind(self.value ** other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value ** other.value, self.unit + '^' + other.unit)
            elif _convertible(other.unit,self.unit):
                return units(self.value ** _converter(other.value, other.unit, self.unit), self.unit + '^' + self.unit)
            elif _convertible(unitBasePower(self.unit)[0], unitBasePower(other.unit)[0]):
                factor = _converter(1, unitBasePower(other.unit)[0], unitBasePower(self.unit)[0])
                return units(self.value ** (other.value * factor), self.unit+'^'+other.unit)
            else:
                return units(self.value ** other.value, self.unit+'^'+other.unit)
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self ** each]
            return tuple(result)
        else:
            powunits = unitBasePower(self.unit)[1] * other
            if powunits == 0:
                powunits = 'dimensionless'
            elif powunits == 1:
                powunits = unitBasePower(self.unit)[0]
            else:
                powunits = unitBasePower(self.unit)[0] + str(powunits)
            return units(self.value ** other, powunits)

    def __sub__(self, other):
        return self.__add__(other * -1)

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        from .units.unitless import dimensionless
        from .units.define import units
        if '.units.' in str(type(other)):
            if self.kind is dimensionless:
                return other.kind(self.value / other.value, other.unit)
            elif other.kind is dimensionless :
                return self.kind(self.value / other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value / other.value, unitDivision(self.unit, other.unit))
            elif _convertible(other.unit, self.unit):
                return units(self.value / _converter(other.value, other.unit, self.unit), unitDivision(self.unit, other.unit))
            elif _convertible(unitBasePower(self.unit)[0], unitBasePower(other.unit)[0]):
                factor = _converter(1, unitBasePower(other.unit)[0], unitBasePower(self.unit)[0])
                return units(self.value / (other.value * factor), unitDivision(self.unit, other.unit))
            else:
                return units(self.value / other.value, unitDivision(self.unit, other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self / each]
            return tuple(result)
        else:
            return units(self.value / other, self.unit)
    def __rtruediv__(self, other):
        from .units.define import units
        return units( other / self.value, self.unit + '-1' )

    def __floordiv__(self, other):
        from .units.unitless import dimensionless
        from .units.define import units
        if '.units.' in str(type(other)):
            if self.kind is dimensionless:
                return other.kind(self.value // other.value, other.unit)
            elif other.kind is dimensionless:
                return self.kind(self.value // other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value // other.value, unitDivision(self.unit, other.unit))
            elif _convertible(other.unit, self.unit):
                return units(self.value // _converter(other.value, other.unit, self.unit), unitDivision(self.unit, other.unit))
            elif _convertible(unitBasePower(self.unit)[0], unitBasePower(other.unit)[0]):
                factor = _converter(1, unitBasePower(other.unit)[0], unitBasePower(self.unit)[0])
                return units(self.value // (other.value * factor), unitDivision(self.unit, other.unit))
            else:
                return units(self.value // other.value, unitDivision(self.unit, other.unit))
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self / each]
            return tuple(result)
        else:
            return self.kind(self.value / other, self.unit)
    def __rfloordiv__(self, other):
        from .units.define import units
        return units( other // self.value, self.unit+'-1' )

    def __mod__(self, other):
        from .units.define import units
        if '.units.' in str(type(other)):
            from .units.unitless import dimensionless
            if self.kind is dimensionless:
                return other.kind(self.value % other.value, self.unit)
            elif other.kind is dimensionless:
                return self.kind(self.value % other.value, self.unit)
            elif self.unit == other.unit:
                return units(self.value % other.value, self.unit)
            elif _convertible(other.unit, self.unit):
                return units(self.value % _converter(other.value, other.unit, self.unit), self.unit)
            elif _convertible(unitBasePower(self.unit)[0], unitBasePower(other.unit)[0]):
                factor = _converter(1, unitBasePower(other.unit)[0], unitBasePower(self.unit)[0])
                return units(self.value % (other.value * factor), self.unit)
            else:
                return units(self.value % other.value, self.unit)
        elif type(other) is tuple:
            result = []
            for each in other:
                result += [self % each]
            return tuple(result)
        else:
            return self.kind(self.value % other,self.unit)

    def __lt__(self, other):
        if type(self) == type(other):
            return self.value < other.convert(self.unit).value
        else:
            msg = "'<' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.', '')   + "'"
            raise TypeError(msg)

    def __le__(self, other):
        if type(self) == type(other):
            return self.value <= other.convert(self.unit).value
        else :
            msg = "'<=' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'"
            raise TypeError(msg)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.value == other.convert(self.unit).value
        else:
            msg = "'==' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'"
            raise TypeError(msg)

    def __ne__(self, other):
        if type(self) == type(other):
            return self.value != other.convert(self.unit).value
        else:
            msg = "'!=' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'"
            raise TypeError(msg)

    def __ge__(self, other):
        if type(self) == type(other):
            return self.value >= other.convert(self.unit).value
        else :
            msg = "'>=' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'"
            raise TypeError(msg)
    def __gt__(self, other):
        if type(self) == type(other):
            return self.value > other.convert(self.unit).value
        else :
            msg = "'>' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'"
            raise TypeError(msg)

    def __len__(self):
        try:
            return len(self.value)
        except:
            return 1

    def __getitem__(self, item):
        if type(item) is int:
            if item >= len(self):
                raise IndexError
        else:
            raise ValueError
        return self.value[item]

    def __iter__(self):
        if type(self.value) in (int, float):
            return _np.array((self.value,)).__iter__()
        else:
            return self.value.__iter__()

    # def __next__(self):
    #     pass

    def getUnit(self):
        return self.unit

    def getValue(self):
        return self.value

    def checkValue(self, value):
        if type(value) in (list, tuple):
            return _np.array(value)
        elif type(value) in (int, float, complex):
            return value
        # elif type(value) is _np.ndarray:
        #     return value
        elif isinstance(value, (Series, DataFrame, np.ndarray)):
             return value
        else:
            raise _WrongValue()

    def checkUnit(self, units):
        if type(units) is not str:
            try:
                units = units.unit
            except:
                raise _WrongUnits
        if units in self.kind.classUnits:
            return units
        else:
            raise _WrongUnits
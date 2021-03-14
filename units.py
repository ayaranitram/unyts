#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: martin
"""
import numpy as np
from ._errors import WrongUnits, WrongValue
from ._operations import unitProduct, unitDivision, unitBasePower
from ._convert import converter as _converter, convertible as _convertible
from ._dictionaries import dictionary

unitClasses = {}

def units(value,units=None) :
    if units is None and '.units.' in str(type(value)) :
        value , units = value.value , value.units    
    if units is None :
        units = 'dimensionless'
    if type(units) is not str :
        raise TypeError("'units' must be a string.")
    units = units.strip()
    for kind in dictionary :
        if units in dictionary[kind] :
            return eval( kind + "(" + str(value) + ",'" + units + "')" )
    return userUnits(value,units)

class _units(object) :
    def __init__(self) :
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
    
    def convert(self,newunit):
        if type(newunit) is not str :
            try :
                newunit = newunit.unit
            except :
                raise WrongUnits
        return self.kind( _converter(self.value,self.unit,newunit) , newunit )
    def to(self,newunit):
        return self.convert(newunit)
    
    def __neg__(self) :
        return self.kind(self.value * -1 , self.unit)
    
    def __bool__(self) :
        if self.kind in [dimensionless,userUnits] :
            return False
        return True
    
    def __abs__(self) :
        return self.kind(abs(self.value),self.unit)
    
    def __add__(self,other) :
        if '.units.' in str(type(other)) :
            if other.kind is self.kind :
                if self.unit == other.unit :
                    return self.kind(self.value + other.value,self.unit)
                else :
                    return self.kind(self.value + _converter(other.value,other.unit,self.unit),self.unit)
            if other.kind is dimensionless :
                return self.kind(self.value + other.value * self.value ,self.unit)
            else : # add different units
                return ( self , other )
        elif type(other) is tuple :
            result , flag = [] , False
            for each in other :
                if type(each) is type(self) :
                    result += [self + each]
                    flag = True
                else :
                    result += each
            return tuple(result) if flag else other + (self,)        
        else :
            return self.kind(self.value + other,self.unit)
    def __radd__(self,other) :
        return self.__add__(other)
        
    def __mul__(self,other) :
        if '.units.' in str(type(other)) :
            if self.kind is dimensionless :
                return other.kind(self.value * other.value,other.unit)
            elif other.kind is dimensionless :
                return self.kind(self.value * other.value,self.unit)
            elif self.unit == other.unit :
                return units(self.value * other.value,unitProduct(self.unit,other.unit))
            elif _convertible(other.unit,self.unit) :
                return units(self.value * _converter(other.value,other.unit,self.unit),unitProduct(self.unit,other.unit))
            elif _convertible( unitBasePower(self.unit)[0] , unitBasePower(self.unit)[0] ) :
                factor = _converter(1,unitBasePower(other.unit)[0],unitBasePower(self.unit)[0])
                return units(self.value * other.value * factor , unitProduct(self.unit,other.unit))
            else :
                return units(self.value * other.value,unitProduct(self.unit,other.unit))
        elif type(other) is tuple :
            result = []
            for each in other :
                result += [self * each]
            return tuple(result)
        else :
            return self.kind(self.value * other,self.unit)
    def __rmul__(self,other) :
        return self.__mul__(other) 
    
    def __pow__(self,other) :
        if '.units.' in str(type(other)) :
            if self.kind is dimensionless :
                return other.kind(self.value ** other.value,other.unit)
            elif other.kind is dimensionless :
                return self.kind(self.value ** other.value,self.unit)
            elif self.unit == other.unit :
                return units(self.value ** other.value,self.unit+'^'+other.unit)
            elif _convertible(other.unit,self.unit) :
                return units(self.value ** _converter(other.value,other.unit,self.unit),self.unit+'^'+self.unit)
            elif _convertible( unitBasePower(self.unit)[0] , unitBasePower(self.unit)[0] ) :
                factor = _converter(1,unitBasePower(other.unit)[0],unitBasePower(self.unit)[0])
                return units(self.value ** (other.value * factor) , self.unit+'^'+other.unit)
            else :
                return units(self.value ** other.value,self.unit+'^'+other.unit)
        elif type(other) is tuple :
            result = []
            for each in other :
                result += [self ** each]
            return tuple(result)
        else :
            return self.kind(self.value ** other,self.unit)
    
    def __sub__(self,other) :
        return self.__add__(other*-1)
    def __rsub__(self,other) :
        return -self + other
    
    def __truediv__(self, other):
        if '.units.' in str(type(other)) :
            if self.kind is dimensionless :
                return other.kind(self.value / other.value,other.unit)
            elif other.kind is dimensionless :
                return self.kind(self.value / other.value,self.unit)
            elif self.unit == other.unit :
                return units(self.value / other.value,unitDivision(self.unit,other.unit))
            elif _convertible(other.unit,self.unit) :
                return units(self.value / _converter(other.value,other.unit,self.unit),unitDivision(self.unit,other.unit))
            elif _convertible( unitBasePower(self.unit)[0] , unitBasePower(self.unit)[0] ) :
                factor = _converter(1,unitBasePower(other.unit)[0],unitBasePower(self.unit)[0])
                return units(self.value / (other.value * factor) , unitDivision(self.unit,other.unit))
            else :
                return units(self.value / other.value,unitDivision(self.unit,other.unit))
        elif type(other) is tuple :
            result = []
            for each in other :
                result += [self / each]
            return tuple(result)
        else :
            return units(self.value / other,self.unit)
    def __rtruediv__(self, other):
        return units( other / self.value , self.unit+'-1' )
    
    def __floordiv__(self, other):
        if '.units.' in str(type(other)) :
            if self.kind is dimensionless :
                return other.kind(self.value // other.value,other.unit)
            elif other.kind is dimensionless :
                return self.kind(self.value // other.value,self.unit)
            elif self.unit == other.unit :
                return units(self.value // other.value,unitDivision(self.unit,other.unit))
            elif _convertible(other.unit,self.unit) :
                return units(self.value // _converter(other.value,other.unit,self.unit),unitDivision(self.unit,other.unit))
            elif _convertible( unitBasePower(self.unit)[0] , unitBasePower(self.unit)[0] ) :
                factor = _converter(1,unitBasePower(other.unit)[0],unitBasePower(self.unit)[0])
                return units(self.value // (other.value * factor) , unitDivision(self.unit,other.unit))
            else :
                return units(self.value // other.value,unitDivision(self.unit,other.unit))
        elif type(other) is tuple :
            result = []
            for each in other :
                result += [self / each]
            return tuple(result)
        else :
            return self.kind(self.value / other,self.unit)
    def __rfloordiv__(self, other):
        return units( other // self.value , self.unit+'-1' )
    
    def __mod__(self, other):
        if '.units.' in str(type(other)) :
            if self.kind is dimensionless :
                return other.kind(self.value % other.value,self.unit)
            elif other.kind is dimensionless :
                return self.kind(self.value % other.value,self.unit)
            elif self.unit == other.unit :
                return units(self.value % other.value,self.unit)
            elif _convertible(other.unit,self.unit) :
                return units(self.value % _converter(other.value,other.unit,self.unit),self.unit)
            elif _convertible( unitBasePower(self.unit)[0] , unitBasePower(self.unit)[0] ) :
                factor = _converter(1,unitBasePower(other.unit)[0],unitBasePower(self.unit)[0])
                return units(self.value % (other.value * factor) , self.unit)
            else :
                return units(self.value % other.value,self.unit)
        elif type(other) is tuple :
            result = []
            for each in other :
                result += [self % each]
            return tuple(result)
        else :
            return self.kind(self.value % other,self.unit)
    
    def __lt__(self,other) :
        if type(self) == type(other) :
            return self.value < other.convert(self.unit).value
        else :
            msg = "'<' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'" 
            raise TypeError(msg)
    def __le__(self,other) :
        if type(self) == type(other) :
            return self.value <= other.convert(self.unit).value
        else :
            msg = "'<=' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'" 
            raise TypeError(msg)
    def __eq__(self,other) :
        if type(self) == type(other) :
            return self.value == other.convert(self.unit).value
        else :
            msg = "'==' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'" 
            raise TypeError(msg)
    def __ne__(self,other) :
        if type(self) == type(other) :
            return self.value != other.convert(self.unit).value
        else :
            msg = "'!=' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'" 
            raise TypeError(msg)
    def __ge__(self,other) :
        if type(self) == type(other) :
            return self.value >= other.convert(self.unit).value
        else :
            msg = "'>=' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'" 
            raise TypeError(msg)
    def __gt__(self,other) :
        if type(self) == type(other) :
            return self.value > other.convert(self.unit).value
        else :
            msg = "'>' not supported between instances of '" +   (str(type(self))[str(type(self)).index("'")+1:len(str(type(self))) - str(type(self))[::-1].index("'")-1]).replace('__main__.','')   + "' and '" +   (str(type(other))[str(type(other)).index("'")+1:len(str(type(other))) - str(type(other))[::-1].index("'")-1]).replace('__main__.','')   + "'" 
            raise TypeError(msg)
            
    def __len__(self) :
        try :
            return len(self.value)
        except :
            return 1
        
    def __getitem__(self, item) :
        if type(item) == int :
            if item >= len(self) :
                raise IndexError
        else :
            raise ValueError
        return self.value[item]
    
    def __iter__(self) :
        if type(self.value) == int or type(self.value) == float :
            return np.array((self.value,)).__iter__()
        else :
            return self.value.__iter__()
        
    # def __next__(self) :
    #     pass

    def getUnit(self) :
        return self.unit
    def getValue(self) :
        return self.value
    
    def checkValue(self,value):
        if type(value) in [ list , tuple ] :
            return np.array(value)
        elif type(value) in [ int , float ] :
            return value
        elif type(value) is np.ndarray :
            return value
        # elif type(value) == pandas.core.frame.DataFrame :
        #     return value
        else :
            raise WrongValue
            
    def checkUnit(self,units) :
        if type(units) != str :
            try :
                units = units.unit
            except :
                raise WrongUnits
        if units in self.kind.classUnits :
            return units
        else :
            raise WrongUnits

class time(_units):
    classUnits = dictionary['time']
    def __init__(self,value,units) :
        self.name = 'time'
        self.kind = time
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class temperature(_units):
    classUnits = dictionary['temperature']
    def __init__(self,value,units) :
        self.name = 'temperature'
        self.kind = temperature
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
        
class pressure(_units):
    classUnits = dictionary['pressure']
    def __init__(self,value,units) :
        self.name = 'pressure'
        self.kind = pressure
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class weight(_units):
    classUnits = dictionary['weight']
    def __init__(self,value,units) :
        self.name = 'weight'
        self.kind = weight
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class length(_units):
    classUnits = dictionary['length']
    def __init__(self,value,units) :
        self.name = 'length'
        self.kind = length
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class area(_units):
    classUnits = dictionary['area']
    def __init__(self,value,units) :
        self.name = 'area'
        self.kind = area
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class volume(_units):
    classUnits = dictionary['volume']
    def __init__(self,value,units) :
        self.name = 'volume'
        self.kind = volume
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class density(_units):
    classUnits = dictionary['density']
    def __init__(self,value,units) :
        self.name = 'density'
        self.kind = density
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
    
class compressibility(_units):
    classUnits = dictionary['compressibility']
    def __init__(self,value,units) :
        self.name = 'compressibility'
        self.kind = compressibility
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class volumeRatio(_units):
    classUnits = dictionary['volumeRatio']
    def __init__(self,value,units) :
        self.name = 'volumeRatio'
        self.kid = volumeRatio
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class rate(_units):
    classUnits = dictionary['rate']
    def __init__(self,value,units) :
        self.name = 'rate'
        self.kind = rate
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class speed(_units):
    classUnits = dictionary['speed']
    def __init__(self,value,units) :
        self.name = 'speed'
        self.kind = speed
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

def velocity(value,units) :
    return speed(value,units)

# class productivityIndex(_units):
#     classUnits = dictionary['productivityIndex']
#     def __init__(self,value,units) :
#         self.name = 'productivityIndex'
#         self.kind = productivityIndex
#         self.value = self.checkValue(value)
#         self.unit = self.checkUnit(units)

# class pressureGradient(_units):
#     classUnits = dictionary['pressureGradient']
#     def __init__(self,value,units) :
#         self.name = 'pressureGradient'
#         self.kind = pressureGradient
#         self.value = self.checkValue(value)
#         self.unit = self.checkUnit(units)


class dimensionless(_units):
    classUnits = dictionary['dimensionless']
    def __init__(self,value,units=None) :
        self.name = 'dimensionless'
        self.kind = dimensionless
        self.value = self.checkValue(value)
        if units is None :
            units = 'dimensionless'
        self.unit = self.checkUnit(units)
        
def customUnits(value,units):
    return userUnits(value,units)

class userUnits(_units):
    classUnits = dictionary['userUnits']
    def __init__(self,value,units) :
        self.name = 'userUnits'
        self.kind = userUnits
        units = units.strip()
        if units not in dictionary['userUnits'] :
            dictionary['userUnits'].append(units)
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

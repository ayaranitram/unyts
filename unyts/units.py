#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:34:59 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
__version__ = '0.1.1'
__release__ = 20220803

from ._dictionaries import dictionary
from ._unit import _units

unitClasses = {}


def units(value, units=None):
    if units is None and '.units.' in str(type(value)):
        value, units = value.value, value.units
    if units is None:
        units = 'dimensionless'
    if type(units) is not str:
        raise TypeError("'units' must be a string.")
    units = units.strip()
    for kind in dictionary:
        if units in dictionary[kind]:
            return eval( kind + "(" + str(value) + ",'" + units + "')" )
    return userUnits(value, units)


class time(_units):
    classUnits = dictionary['time']
    def __init__(self, value, units):
        self.name = 'time'
        self.kind = time
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class temperature(_units):
    classUnits = dictionary['temperature']
    def __init__(self, value, units):
        self.name = 'temperature'
        self.kind = temperature
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class pressure(_units):
    classUnits = dictionary['pressure']
    def __init__(self, value, units):
        self.name = 'pressure'
        self.kind = pressure
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class weight(_units):
    classUnits = dictionary['weight']
    def __init__(self, value, units):
        self.name = 'weight'
        self.kind = weight
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class length(_units):
    classUnits = dictionary['length']
    def __init__(self, value, units):
        self.name = 'length'
        self.kind = length
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class area(_units):
    classUnits = dictionary['area']
    def __init__(self, value, units):
        self.name = 'area'
        self.kind = area
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class volume(_units):
    classUnits = dictionary['volume']
    def __init__(self, value, units):
        self.name = 'volume'
        self.kind = volume
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class density(_units):
    classUnits = dictionary['density']
    def __init__(self, value, units):
        self.name = 'density'
        self.kind = density
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class compressibility(_units):
    classUnits = dictionary['compressibility']
    def __init__(self, value, units):
        self.name = 'compressibility'
        self.kind = compressibility
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class volumeRatio(_units):
    classUnits = dictionary['volumeRatio']
    def __init__(self, value, units):
        self.name = 'volumeRatio'
        self.kid = volumeRatio
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class rate(_units):
    classUnits = dictionary['rate']
    def __init__(self, value, units):
        self.name = 'rate'
        self.kind = rate
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

class speed(_units):
    classUnits = dictionary['speed']
    def __init__(self, value, units):
        self.name = 'speed'
        self.kind = speed
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)

def velocity(value, units):
    return speed(value, units)

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
    def __init__(self, value, units=None):
        self.name = 'dimensionless'
        self.kind = dimensionless
        self.value = self.checkValue(value)
        if units is None :
            units = 'dimensionless'
        self.unit = self.checkUnit(units)

def customUnits(value, units):
    return userUnits(value,units)

class userUnits(_units):
    classUnits = dictionary['userUnits']
    def __init__(self, value, units):
        self.name = 'userUnits'
        self.kind = userUnits
        units = units.strip()
        if units not in dictionary['userUnits']:
            dictionary['userUnits'].append(units)
        self.value = self.checkValue(value)
        self.unit = self.checkUnit(units)
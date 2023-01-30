# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 09:41:45 2023

@author: martin
"""
__version__ = '0.0.0'
__release__ = 20230128

from unyts import units, Unit

# Data
bit = units(1, 'b')
byte = units(1, 'B')

# Length
millimetre = units(1, 'mm')
millimeter = millimetre
centimeter = units(1, 'cm')
meter = units(1, 'm')
kilometre = units(1, 'km')
kilometer = kilometre
thou = units(1, 'th')
tenth = units(1, 'te')
inch = units(1, 'in')
foot = units(1, 'ft')
feet = foot
chain = units(1, 'ch')
yard = units(1, 'yd')
furlong = units(1, 'fur')
mile = units(1, 'mi')
league = units(1, 'lea')

# Area
acre = units(1, 'acre')

# Volume
barrel = units(1, 'stb')
stb = barrel
sm3 = units(1, 'sm3')
litre = units(1, 'l')
gill = units(1, 'gi')
pint = units(1, 'pt')
quart = units(1, 'qt')
gallonUS = units(1, 'galUS')
gallonUK = units(1, 'galUK')

# Weigh
gram = units(1, 'g')
kilogram = units(1, 'kg')
grain = units(1, 'gr')
pennyweight = units(1, 'pwt')
dram = units(1, 'dr')
ounce = Unit(1, 'oz')
pound = units(1, 'lb')
quarter = units(1, 'qrt')
ton = units(1, 'long ton')

# Time
second = units(1, 'sec')
minute = units(1, 'min')
hour = units(1, 'hour')
day = units(1, 'day')
week = units(1, 'week')
month = units(1, 'month')
year = units(1, 'year')

# Temperature
celsius = units(1, 'deg C')
fahrenheit = units(1, 'deg F')
rankine = units(1, 'deg R')
kelvin = units(1, 'deg K')

# Pressure
pascal = units(1, 'Pa')
kilopascal = units(1, 'kPa')
torr = units(1, 'mmHg')
mmgh = torr
psi = units(1, 'psia')
bar = units(1, 'barsa')
atmosphere = units(1, 'atm')

# Force
newton = units(1, 'N')
dyne = units(1, 'dyne')

# Energy
joule = units(1, 'J')
btu = units(1, 'btu')

# Power
horsepower = units(1, 'hp')
watt = units(1, 'W')

volt = units(1, 'V')
ampere = units(1, 'A')
ohm = units(1, 'Ω')
siemen = units(1, '℧')
farad = units(1, 'Farad')
coulomb = units(1, 'Q')
henry = units(1, 'H')

# Frequency
hertz = units(1, 'Hz')
rpm = units(1, 'RPM')

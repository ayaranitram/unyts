#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 23:15:37 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.1.1'
__release__ = 20250502

from unyts import network
from ..dictionaries import SpeedOfLight, StandardEarthGravity, StandardAirDensity


def equality(x):
    """
    conversion of lambda:
      x: x
    """
    return x

def inverse(x):
    """"
        conversion of lambda:
          x: 1 / x
        """
    return 1 / x

def fraction__to__percentage(fraction):
    """"
    conversion of lambda: 
      x: x * 100
    """
    x = fraction
    return x * 100

def percentage__to__fraction(percentage):
    """"
    conversion of lambda: 
      p: p / 100
    """
    p = percentage
    return p / 100

def second__to__millisecond(second):
    """"
    conversion of lambda: 
      t: t * 1000
    """
    t = second
    return t * 1000

def minute__to__second(minute):
    """"
    conversion of lambda: 
      t: t * 60
    """
    t = minute
    return t * 60

def hour__to__minute(hour):
    """"
    conversion of lambda: 
      t: t * 60
    """
    t = hour
    return t * 60

def day__to__hour(day):
    """"
    conversion of lambda: 
      t: t * 24
    """
    t = day
    return t * 24

def day__to__month(day):
    """"
    conversion of lambda: 
      t: t / 365.25 * 12
    """
    t = day
    return t / 365.25 * 12

def week__to__day(week):
    """"
    conversion of lambda: 
      t: t * 7
    """
    t = week
    return t * 7

def year__to__month(year):
    """"
    conversion of lambda: 
      t: t * 12
    """
    t = year
    return t * 12

def year__to__day(year):
    """"
    conversion of lambda: 
      t: t * 36525 / 100
    """
    t = year
    return t * 36525 / 100

def lustrum__to__year(lustrum):
    """"
    conversion of lambda: 
      t: t * 5
    """
    t = lustrum
    return t * 5

def decade__to__year(decade):
    """"
    conversion of lambda: 
      t: t * 10
    """
    t = decade
    return t * 10

def century__to__year(century):
    """"
    conversion of lambda: 
      t: t * 100
    """
    t = century
    return t * 100

def Celsius__to__Kelvin(Celsius):
    """"
    conversion of lambda: 
      t: t + 273.15
    """
    t = Celsius
    return t + 273.15

def Kelvin__to__Celsius(Kelvin):
    """"
    conversion of lambda: 
      t: t - 273.15
    """
    t = Kelvin
    return t - 273.15

def Celsius__to__Fahrenheit(Celsius):
    """"
    conversion of lambda: 
      t: t * 9 / 5 + 32
    """
    t = Celsius
    return t * 9 / 5 + 32

def Fahrenheit__to__Celsius(Fahrenheit):
    """"
    conversion of lambda: 
      t: (t - 32) * 5 / 9
    """
    t = Fahrenheit
    return (t - 32) * 5 / 9

def Fahrenheit__to__Rankine(Fahrenheit):
    """"
    conversion of lambda: 
      t: t + 459.67
    """
    t = Fahrenheit
    return t + 459.67

def Rankine__to__Fahrenheit(Rankine):
    """"
    conversion of lambda: 
      t: t - 459.67
    """
    t = Rankine
    return t - 459.67

def Rankine__to__Kelvin(Rankine):
    """"
    conversion of lambda: 
      t: t * 5 / 9
    """
    t = Rankine
    return t * 5 / 9

def Kelvin__to__Rankine(Kelvin):
    """"
    conversion of lambda: 
      t: t * 9 / 5
    """
    t = Kelvin
    return t * 9 / 5

def yard__to__meter(yard):
    """"
    conversion of lambda: 
      d: d * 9144 / 10000
    """
    d = yard
    return d * 9144 / 10000

def foot__to__meter(yard):
    """"
    conversion of lambda:
      d: d * 3048 / 10000
    """
    d = yard
    return d * 3048 / 10000

def inch__to__thou(inch):
    """"
    conversion of lambda: 
      d: d * 1000
    """
    d = inch
    return d * 1000

def inch__to__tenth(inch):
    """"
    conversion of lambda: 
      d: d * 10
    """
    d = inch
    return d * 10

def foot__to__inch(foot):
    """"
    conversion of lambda: 
      d: d * 12
    """
    d = foot
    return d * 12

def yard__to__foot(yard):
    """"
    conversion of lambda: 
      d: d * 3
    """
    d = yard
    return d * 3

def chain__to__yard(chain):
    """"
    conversion of lambda: 
      d: d * 22
    """
    d = chain
    return d * 22

def furlong__to__chain(furlong):
    """"
    conversion of lambda: 
      d: d * 10
    """
    d = furlong
    return d * 10

def mile__to__furlong(mile):
    """"
    conversion of lambda: 
      d: d * 8
    """
    d = mile
    return d * 8

def league__to__mile(league):
    """"
    conversion of lambda: 
      d: d * 3
    """
    d = league
    return d * 3

def nautical_league__to__nautical_mile(nautical_league):
    """"
    conversion of lambda: 
      d: d * 3
    """
    d = nautical_league
    return d * 3

def nautical_mile__to__meter(nautical_mile):
    """"
    conversion of lambda: 
      d: d * 1852
    """
    d = nautical_mile
    return d * 1852

def rod__to__yard(rod):
    """"
    conversion of lambda: 
      d: d * 55 / 10
    """
    d = rod
    return d * 55 / 10

def astronomical_unit__to__meter(astronomical_unit):
    """"
    conversion of lambda: 
      d: d * 149597870700
    """
    d = astronomical_unit
    return d * 149597870700

def parsec__to__astronomical_unit(parsec):
    """"
    conversion of lambda: 
      d: d * 206265
    """
    d = parsec
    return d * 206265

def light_year__to__meter(light_year):
    """"
    conversion of lambda: 
      d: d * SpeedOfLight * 365.25 * 24 * 60
    """
    d = light_year
    return d * SpeedOfLight * 365.25 * 24 * 60

def scandinavian_mile__to__kilometer(scandinavian_mile):
    """
    conversion of lambda:
        d: d * 10
    """
    d = scandinavian_mile
    return d * 10

def mile_per_hour__to__kilometer_per_hour(mile_per_hour):
    """"
    conversion of lambda: 
      v: v * 8 * 10 * 22 * 9144 / 10000 / 1000
    """
    v = mile_per_hour
    return v * 8 * 10 * 22 * 9144 / 10000 / 1000

def square_kilometer__to__square_meter(square_kilometer):
    """"
    conversion of lambda: 
      d: d * 1000000
    """
    d = square_kilometer
    return d * 1000000

def square_mile__to__acre(square_mile):
    """"
    conversion of lambda: 
      d: d * 640
    """
    d = square_mile
    return d * 640

def acre__to__square_yard(acre):
    """"
    conversion of lambda: 
      d: d * 4840
    """
    d = acre
    return d * 4840

def square_rod__to__square_yard(square_rod):
    """"
    conversion of lambda: 
      d: d * 3025 / 100
    """
    d = square_rod
    return d * 3025 / 100

def square_yard__to__square_foot(square_yard):
    """"
    conversion of lambda: 
      d: d * 9
    """
    d = square_yard
    return d * 9

def square_foot__to__square_inch(square_foot):
    """"
    conversion of lambda: 
      d: d * 144
    """
    d = square_foot
    return d * 144

def square_foot__to__square_meter(square_foot):
    """"
    conversion of lambda: 
      d: d * (3048 ** 2) / (10000 ** 2)
    """
    d = square_foot
    return d * (3048 ** 2) / (10000 ** 2)

def square_inch__to__square_thou(square_inch):
    """"
    conversion of lambda: 
      d: d * (1000 ** 2)
    """
    d = square_inch
    return d * (1000 ** 2)

def square_inch__to__square_tenth(square_inch):
    """"
    conversion of lambda: 
      d: d * (10 ** 2)
    """
    d = square_inch
    return d * (10 ** 2)

def square_chain__to__square_yard(square_chain):
    """"
    conversion of lambda: 
      d: d * (22 ** 2)
    """
    d = square_chain
    return d * (22 ** 2)

def square_furlong__to__square_chain(square_furlong):
    """"
    conversion of lambda: 
      d: d * (10 ** 2)
    """
    d = square_furlong
    return d * (10 ** 2)

def square_mile__to__square_furlong(square_mile):
    """"
    conversion of lambda: 
      d: d * (8 ** 2)
    """
    d = square_mile
    return d * (8 ** 2)

def square_league__to__square_mile(square_league):
    """"
    conversion of lambda: 
      d: d * (3 ** 2)
    """
    d = square_league
    return d * (3 ** 2)

def Darcy__to__µm2(Darcy):
    """"
    conversion of lambda: 
      d: d * 0.9869233
    """
    d = Darcy
    return d * 0.9869233

def litre__to__cubic_centimeter(litre):
    """"
    conversion of lambda: 
      v: v * 1000
    """
    v = litre
    return v * 1000

def gill__to__fluid_ounce(gill):
    """"
    conversion of lambda: 
      v: v * 4
    """
    v = gill
    return v * 4

def pint__to__gill(pint):
    """"
    conversion of lambda: 
      v: v * 4
    """
    v = pint
    return v * 4

def quart__to__pint(quart):
    """"
    conversion of lambda: 
      v: v * 2
    """
    v = quart
    return v * 2

def gallonUS__to__fluid_ounce(gallonUS):
    """"
    conversion of lambda: 
      v: v * 128
    """
    v = gallonUS
    return v * 128

def gallonUS__to__quart(gallonUS):
    """"
    conversion of lambda: 
      v: v * 4
    """
    v = gallonUS
    return v * 4

def gallonUS__to__cubic_inch(gallonUS):
    """"
    conversion of lambda: 
      v: v * 231
    """
    v = gallonUS
    return v * 231

def gallonUK__to__quartUK(gallonUK):
    """"
    conversion of lambda: 
      v: v * 4
    """
    v = gallonUK
    return v * 4

def gallonUK__to__fluid_ounce_UK(gallonUK):
    """"
    conversion of lambda: 
      v: v * 160
    """
    v = gallonUK
    return v * 160

def gallonUK__to__litre(gallonUK):
    """"
    conversion of lambda: 
      v: v * 4.54609
    """
    v = gallonUK
    return v * 4.54609

def gillUK__to__fluid_ounce_UK(gillUK):
    """"
    conversion of lambda: 
      v: v * 4
    """
    v = gillUK
    return v * 4

def pintUK__to__gillUK(pintUK):
    """"
    conversion of lambda: 
      v: v * 4
    """
    v = pintUK
    return v * 4

def quartUK__to__pintUK(quartUK):
    """"
    conversion of lambda: 
      v: v * 2
    """
    v = quartUK
    return v * 2

def gallonUK__to__liter(gallonUK):
    """"
    conversion of lambda: 
      v: v * 4.54609
    """
    v = gallonUK
    return v * 4.54609

def cubic_foot__to__cubic_meter(cubic_foot):
    """"
    conversion of lambda: 
      v: v * (3048 ** 3) / (10000 ** 3)
    """
    v = cubic_foot
    return v * (3048 ** 3) / (10000 ** 3)

def standard_cubic_foot__to__standard_cubic_meter(standard_cubic_foot):
    """"
    conversion of lambda: 
      v: v * (3048 ** 3) / (10000 ** 3)
    """
    v = standard_cubic_foot
    return v * (3048 ** 3) / (10000 ** 3)

def standard_cubic_meter__to__standard_cubic_foot(standard_cubic_meter):
    """"
    conversion of lambda:
      v: v / (3048 ** 3) * (10000 ** 3)
    """
    v = standard_cubic_meter
    return v / (3048 ** 3) * (10000 ** 3)


def standard_barrel__to__USgal(standard_barrel):
    """"
    conversion of lambda: 
      v: v * 42
    """
    v = standard_barrel
    return v * 42

def standard_cubic_meter__to__standard_barrel(standard_cubic_meter):
    """"
    conversion of lambda: 
      v: v * 6.289814
    """
    v = standard_cubic_meter
    return v * 6.289814

def standard_barrel__to__standard_cubic_foot(standard_barrel):
    """"
    conversion of lambda: 
      v: v * 5.614584
    """
    v = standard_barrel
    return v * 5.614584

def reservoir_cubic_meter__to__reservoir_barrel(reservoir_cubic_meter):
    """"
    conversion of lambda: 
      v: v * 6.289814
    """
    v = reservoir_cubic_meter
    return v * 6.289814

def reservoir_cubic_meter__to__standard_cubic_meter(reservoir_cubic_meter):
    """"
    conversion of lambda: 
      v: v / network.get_fvf()
    """
    v = reservoir_cubic_meter
    return v / network.get_fvf()

def cubic_inch__to__cubic_thou(cubic_inch):
    """"
    conversion of lambda: 
      d: d * (1000 ** 3)
    """
    d = cubic_inch
    return d * (1000 ** 3)

def cubic_inch__to__cubic_tenth(cubic_inch):
    """"
    conversion of lambda: 
      d: d * (10 ** 3)
    """
    d = cubic_inch
    return d * (10 ** 3)

def cubic_foot__to__cubic_inch(cubic_foot):
    """"
    conversion of lambda: 
      d: d * (12 ** 3)
    """
    d = cubic_foot
    return d * (12 ** 3)

def cubic_yard__to__cubic_foot(cubic_yard):
    """"
    conversion of lambda: 
      d: d * (3 ** 3)
    """
    d = cubic_yard
    return d * (3 ** 3)

def cubic_chain__to__cubic_yard(cubic_chain):
    """"
    conversion of lambda: 
      d: d * (22 ** 3)
    """
    d = cubic_chain
    return d * (22 ** 3)

def cubic_furlong__to__cubic_chain(cubic_furlong):
    """"
    conversion of lambda: 
      d: d * (10 ** 3)
    """
    d = cubic_furlong
    return d * (10 ** 3)

def cubic_mile__to__cubic_furlong(cubic_mile):
    """"
    conversion of lambda: 
      d: d * (8 ** 3)
    """
    d = cubic_mile
    return d * (8 ** 3)

def cubic_league__to__cubic_mile(cubic_league):
    """"
    conversion of lambda: 
      d: d * (3 ** 3)
    """
    d = cubic_league
    return d * (3 ** 3)

def psi_gauge__to__absolute_psi(psi_gauge):
    """"
    conversion of lambda: 
      p: p + 14.6959
    """
    p = psi_gauge
    return p + 14.6959

def absolute_psi__to__psi_gauge(absolute_psi):
    """"
    conversion of lambda: 
      p: p - 14.6959
    """
    p = absolute_psi
    return p - 14.6959

def bar_gauge__to__absolute_bar(bar_gauge):
    """"
    conversion of lambda: 
      p: p + 1.01325
    """
    p = bar_gauge
    return p + 1.01325

def absolute_bar__to__bar_gauge(absolute_bar):
    """"
    conversion of lambda: 
      p: p - 1.01325
    """
    p = absolute_bar
    return p - 1.01325

def absolute_bar__to__absolute_psi(absolute_bar):
    """"
    conversion of lambda: 
      p: p * 14.50377377322
    """
    p = absolute_bar
    return p * 14.50377377322

def bar_gauge__to__psi_gauge(bar_gauge):
    """"
    conversion of lambda: 
      p: p * 14.50377377322
    """
    p = bar_gauge
    return p * 14.50377377322

def bar__to__psi(bar):
    """"
    conversion of lambda: 
      p: p * 14.50377377322
    """
    p = bar
    return p * 14.50377377322

def psi__to__bar(psi):
    """"
    conversion of lambda: 
      p: p / 14.50377377322
    """
    p = psi
    return p / 14.50377377322

def absolute_bar__to__Pascal(absolute_bar):
    """"
    conversion of lambda: 
      p: p * 100000
    """
    p = absolute_bar
    return p * 100000

def atmosphere__to__Pascal(atmosphere):
    """"
    conversion of lambda: 
      p: p * 101325
    """
    p = atmosphere
    return p * 101325

def atmosphere__to__Torr(atmosphere):
    """"
    conversion of lambda: 
      p: p * 760
    """
    p = atmosphere
    return p * 760

def atmosphere__to__absolute_bar(atmosphere):
    """"
    conversion of lambda:
      p: p * 101325 / 100000
    """
    p = atmosphere
    return p * 101325 / 100000

def absolute_bar__to__kilogram_slash_square_centimeter(absolute_bar):
    """"
    conversion of lambda: 
      p: p * (10.0 / StandardEarthGravity)
    """
    p = absolute_bar
    return p * (10.0 / StandardEarthGravity)

def grain__to__milligrams(grain):
    """"
    conversion of lambda: 
      w: w * 64.7989
    """
    w = grain
    return w * 64.7989

def pennyweight__to__grain(pennyweight):
    """"
    conversion of lambda: 
      w: w * 24
    """
    w = pennyweight
    return w * 24

def dram__to__pound(dram):
    """"
    conversion of lambda: 
      w: w / 256
    """
    w = dram
    return w / 256

def stone__to__pound(stone):
    """"
    conversion of lambda: 
      w: w * 14
    """
    w = stone
    return w * 14

def quarter__to__stone(quarter):
    """"
    conversion of lambda: 
      w: w * 2
    """
    w = quarter
    return w * 2

def weight_ounce__to__dram(weight_ounce):
    """"
    conversion of lambda: 
      w: w * 16
    """
    w = weight_ounce
    return w * 16

def pound__to__weight_ounce(pound):
    """"
    conversion of lambda: 
      w: w * 16
    """
    w = pound
    return w * 16

def long_hundredweight__to__quarter(long_hundredweight):
    """"
    conversion of lambda: 
      w: w * 4
    """
    w = long_hundredweight
    return w * 4

def short_hundredweight__to__pound(short_hundredweight):
    """"
    conversion of lambda: 
      w: w * 100
    """
    w = short_hundredweight
    return w * 100

def short_ton__to__short_hundredweight(short_ton):
    """"
    conversion of lambda: 
      w: w * 20
    """
    w = short_ton
    return w * 20

def long_ton__to__long_hundredweight(long_ton):
    """"
    conversion of lambda: 
      w: w * 20
    """
    w = long_ton
    return w * 20

def metric_ton__to__kilogram(metric_ton):
    """"
    conversion of lambda: 
      w: w * 1000
    """
    w = metric_ton
    return w * 1000

def kilogram__to__gram(kilogram):
    """"
    conversion of lambda: 
      w: w * 1000
    """
    w = kilogram
    return w * 1000

def pound__to__kilogram(pound):
    """"
    conversion of lambda: 
      w: w * 45359237 / 100000000
    """
    w = pound
    return w * 45359237 / 100000000

def pound__to__gram(pound):
    """"
    conversion of lambda:
      w: w * 45359237 / 100000
    """
    w = pound
    return w * 45359237 / 100000

def kilogram_mass__to__kilogram_force(kilogram_mass):
    """"
    conversion of lambda: 
      f: f * StandardEarthGravity
    """
    f = kilogram_mass
    return f * StandardEarthGravity

def kilogram_force__to__kilogram_mass(kilogram_force):
    """"
    conversion of lambda: 
      f: f / StandardEarthGravity
    """
    f = kilogram_force
    return f / StandardEarthGravity

def Dyne__to__Newton(Dyne):
    """"
    conversion of lambda: 
      f: f * 1E-5
    """
    f = Dyne
    return f * 1E-5

def Newton__to__Dyne(Newton):
    """"
    conversion of lambda: 
      f: f * 1E5
    """
    f = Newton
    return f * 1E5

def Joule__to__gram_calorie(Joule):
    """"
    conversion of lambda: 
      e: e / 4.184
    """
    e = Joule
    return e / 4.184

def Kilojoule__to__Joule(Kilojoule):
    """"
    conversion of lambda: 
      e: e * 1000
    """
    e = Kilojoule
    return e * 1000

def Kilojoule__to__kilowatt_hour(Kilojoule):
    """"
    conversion of lambda: 
      e: e / 3600
    """
    e = Kilojoule
    return e / 3600

def Kilojoule__to__British_thermal_unit(Kilojoule):
    """"
    conversion of lambda: 
      e: e / 1.055
    """
    e = Kilojoule
    return e / 1.055

def Horsepower__to__Watt(Horsepower):
    """"
    conversion of lambda: 
      e: e * 745.699872
    """
    e = Horsepower
    return e * 745.699872

def API__to__SgO(API):
    """"
    conversion of lambda: 
      d: 141.5 / (131.5 + d)
    """
    d = API
    return 141.5 / (131.5 + d)

def SgO__to__API(SgO):
    """"
    conversion of lambda: 
      d: 141.5 / d - 131.5
    """
    d = SgO
    return 141.5 / d - 131.5

def API__to__g_slash_cc(API):
    """"
    conversion of lambda: 
      d: 141.5 / (131.5 + d)
    """
    d = API
    return 141.5 / (131.5 + d)

def g_slash_cc__to__API(g_slash_cc):
    """"
    conversion of lambda: 
      d: 141.5 / d - 131.5
    """
    d = g_slash_cc
    return 141.5 / d - 131.5

def SgG__to__kg_slash_m3(SgG):
    """"
    conversion of lambda: 
      d: d * StandardAirDensity
    """
    d = SgG
    return d * StandardAirDensity

def psia_slash_ft__to__lb_slash_ft3(psia_slash_ft):
    """"
    conversion of lambda: 
      d: d * 144
    """
    d = psia_slash_ft
    return d * 144

def psi_slash_ft__to__lb_slash_ft3(psi_slash_ft):
    """"
    conversion of lambda: 
      d: d * 144
    """
    d = psi_slash_ft
    return d * 144

def psig_slash_ft__to__lb_slash_ft3(psig_slash_ft):
    """"
    conversion of lambda: 
      d: d * 144
    """
    d = psig_slash_ft
    return d * 144

def bara_slash_m__to__kg_slash_m3(bara_slash_m):
    """"
    conversion of lambda: 
      d: d * 100000 / StandardEarthGravity
    """
    d = bara_slash_m
    return d * 100000 / StandardEarthGravity

def bar_slash_m__to__kg_slash_m3(bar_slash_m):
    """"
    conversion of lambda: 
      d: d * 100000 / StandardEarthGravity
    """
    d = bar_slash_m
    return d * 100000 / StandardEarthGravity

def barg_slash_m__to__kg_slash_m3(barg_slash_m):
    """"
    conversion of lambda: 
      d: d * 100000 / StandardEarthGravity
    """
    d = barg_slash_m
    return d * 100000 / StandardEarthGravity

def g_slash_cm3__to__lb_slash_ft3(g_slash_cm3):
    """"
    conversion of lambda: 
      d: d * 62.427960576144606
    """
    d = g_slash_cm3
    return d * 62.427960576144606

def lb_slash_ft3__to__lb_slash_stb(lb_slash_ft3):
    """"
    conversion of lambda: 
      d: d * 5.614584
    """
    d = lb_slash_ft3
    return d * 5.614584

def Pa_star_s__to__Poise(Pa_star_s):
    """"
    conversion of lambda: 
      v: v * 10
    """
    v = Pa_star_s
    return v * 10

def byte__to__bit(byte):
    """"
    conversion of lambda: 
      d: d * 8
    """
    d = byte
    return d * 8

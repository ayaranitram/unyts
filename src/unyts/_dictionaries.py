#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:14:51 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__all__ = ['dictionary','SI','OGF','DATA','StandardAirDensity','StandadEarthGravity']
__version__ = '0.1.0'
__release__ = 20220524

StandardAirDensity = 1.225 # Kg/m3 or g/cc
StandadEarthGravity = 9.80665 # m/s2 or 980.665 cm/s2 from

# the dictionary that contains all the units definitions
dictionary = {}

# Sistema Internacional
SI = {
    'Y' : (lambda X: X*1.0E+24,lambda X: X*1.0E+48,lambda X: X*1.0E+72) , # yotta
    'Z' : (lambda X: X*1.0E+21,lambda X: X*1.0E+42,lambda X: X*1.0E+63) , # zetta
    'E' : (lambda X: X*1.0E+18,lambda X: X*1.0E+36,lambda X: X*1.0E+54) , # exa
    'P' : (lambda X: X*1.0E+15,lambda X: X*1.0E+30,lambda X: X*1.0E+46) , # peta
    'T' : (lambda X: X*1.0E+12,lambda X: X*1.0E+24,lambda X: X*1.0E+36) , # tera
    'G' : (lambda X: X*1.0E+09,lambda X: X*1.0E+18,lambda X: X*1.0E+27) , # giga
    'M' : (lambda X: X*1.0E+06,lambda X: X*1.0E+12,lambda X: X*1.0E+18) , # mega
    'K' : (lambda X: X*1.0E+03,)*3 , # with uppercase K is commonly used to express x1000
    'k' : (lambda X: X*1.0E+03,lambda X: X*1.0E+06,lambda X: X*1.0E+09) , # kilo
    'h' : (lambda X: X*1.0E+02,lambda X: X*1.0E+04,lambda X: X*1.0E+06) , # hecto
    'd' : (lambda X: X*1.0E-01,lambda X: X*1.0E-02,lambda X: X*1.0E-03) , # deci
    'c' : (lambda X: X*1.0E-02,lambda X: X*1.0E-04,lambda X: X*1.0E-06) , # centi
    'm' : (lambda X: X*1.0E-03,lambda X: X*1.0E-06,lambda X: X*1.0E-09) , # mili
    'µ' : (lambda X: X*1.0E-06,lambda X: X*1.0E-12,lambda X: X*1.0E-18) , # micro
    'u' : (lambda X: X*1.0E-06,lambda X: X*1.0E-12,lambda X: X*1.0E-18) , # micro
    'n' : (lambda X: X*1.0E-09,lambda X: X*1.0E-18,lambda X: X*1.0E-27) , # nano
    'p' : (lambda X: X*1.0E-12,lambda X: X*1.0E-24,lambda X: X*1.0E-36) , # pico
    'f' : (lambda X: X*1.0E-15,lambda X: X*1.0E-30,lambda X: X*1.0E-45) , # femto
    'a' : (lambda X: X*1.0E-18,lambda X: X*1.0E-36,lambda X: X*1.0E-54) , # atto
    'z' : (lambda X: X*1.0E-21,lambda X: X*1.0E-42,lambda X: X*1.0E-63) , # zepto
    'y' : (lambda X: X*1.0E-24,lambda X: X*1.0E-48,lambda X: X*1.0E-72) , # yocto
    }
SI_order = (('length','pressure','weight','mass','time',),('area',),('rate','volume',),)
DATA = {
    'Y' : (lambda X: X*1.0E+24,lambda X: X*2**80) , # yotta
    'Z' : (lambda X: X*1.0E+21,lambda X: X*2**70) , # zetta
    'E' : (lambda X: X*1.0E+18,lambda X: X*2**60) , # exa
    'P' : (lambda X: X*1.0E+15,lambda X: X*2**50) , # peta
    'T' : (lambda X: X*1.0E+12,lambda X: X*2**40) , # tera
    'G' : (lambda X: X*1.0E+09,lambda X: X*2**30) , # giga
    'M' : (lambda X: X*1.0E+06,lambda X: X*2**20) , # mega
    'K' : (lambda X: X*1.0E+03,lambda X: X*2**10) , # kilo with uppercase K because it is very common
    'k' : (lambda X: X*1.0E+03,lambda X: X*2**10) , # kilo
    }
DATA_order = (('dataBIT',),('dataBYTE',))


# Oil & Gas Field Unit System
OGF = { 'M' : (None,None,lambda X: X*1.0E+03),
        'MM' : (None,None,lambda X: X*1.0E+06),
        'B' : (None,None,lambda X: X*1.0E+09),
        'T' : (None,None,lambda X: X*1.0E+12),
    }
OGF_order = (tuple(),tuple,('volume','rate',))


dictionary['time'] = []
dictionary['time_NAMES_UPPER_PLURALwS_REVERSE'] = {
    'nanosecond': ('ns',),
    'millisecond': ('ms',),
    'second': ('s', 'sec'),
    'minute': ('min',),
    'hour': ('h', 'hr'),
    'day': ('d', 'día', 'días', 'DíA'),
    'week': ('w', 'we'),
    'month': ('mo', 'mes', 'meses'),
    'year': ('y', 'año'),
    'lustrum': tuple(),
    'decade': tuple(),
    'century': ('centuries',),
    }
dictionary['time_SI'] = ('s',)

dictionary['temperature'] = ['C', 'K', 'F', 'R']
dictionary['temperature_NAMES'] = {
    'Celsius': ('Centigrades', 'C', 'DEG C', 'DEGREES C'),
    'Fahrenheit': ('F','DEG F','DEGREES F'),
    'Rankine': ('R','DEG R','DEGREES R'),
    'Kelvin': ('K','DEG K','DEGREES K')
    }

dictionary['length'] = []
dictionary['length_NAMES_UPPER_REVERSE'] = {'meter': ('m', 'meter', 'metro')}
dictionary['length_SI'] = ('m', 'l')  # litre is volumen but the conversion of SI prefixes is linear
dictionary['length_UK_NAMES_UPPER_REVERSE'] = {
    'thou': ('th',),
    'inch': ('in', '"'),
    'foot': ('feet','ft',"'"),
    'yard': ('yd',),
    'chain': ('ch',),
    'rod': ('rd',),
    'furlong': ('fur',),
    'mile': ('mi',),
    'league': ('lea',),
    'nautical mile': ('nmi',),
    'nautical league': ('nlea',),
    }

dictionary['area'] = []
dictionary['area_NAMES_UPPER_REVERSE'] = {'square meter': ('sq m', 'm2', 'sqmeter', 'm*m', 'm3/m')}
dictionary['area_SI'] = ('m2',)
dictionary['area_UK_NAMES_UPPER_REVERSE'] = {
    'square mile': ('sq mi','mi2','sqmile','mi*mi'),
    'acre': tuple(),
    'square rod': ('sq rd', 'sqrd', 'rd2', 'rd*rd'),
    'square yard': ('sq yd', 'sqyd', 'yd2', 'yd*yd'),
    'square foot': ('sq ft', 'sqft', 'ft2', 'ft*ft', 'ft3/ft'),
    'square inch': ('sq in', 'sqin', 'in2', 'in*in', 'in3/in')
    }

dictionary['volume'] = []
dictionary['volume_SI_UPPER_REVERSE'] = ('m3', 'sm3', 'stm3', 'rm3',)  # 'l' # litre is volumen but the conversion of SI prefixes is linear
dictionary['volume_UK_NAMES_UPPER_REVERSE_PLURALwS'] = {
    'fuild ounce': ('fl oz','oz','ounce'),
    'gill': ('gi',),
    'pint': ('pt',),
    'quart': ('qt',),
    'gallonUK': ('gal', 'galUK', 'UKgal', 'UKgallon', 'gallon'),
    'gallonUS': ('gal', 'galUS', 'USgal', 'USgallon', 'gallon'),
    }
dictionary['volume_NAMES_UPPER_REVERSE_PLURALwS_SPACES'] = {
    'litre': ('l', 'liter', 'litro'),
    'mililitre': ('ml', 'mililiter', 'cubic centimeter'),
    'centilitre': ('cl', 'centiliter'),
    'decilitre': ('dl', 'deciliter') ,
    'cubic meter': ('CM', 'm3'),
    'standard cubic meter': ('scm', 'sm3', 'stm3', 'm3'),
    'cubic centimeter': ( 'cc', 'cm3', 'standard cubic centimeter'),
    'standard cubic centimeter': ( 'scc', 'scm3'),
    'reservoir cubic meter': ('rm3',),
    'reservoir cubic centimeter': ( 'rcc', 'rcm3'),
    'cubic foot': ('cubic feet', 'ft3', 'cf'),
    'standard cubic foot': ('scf', 'cf'),
    'cubic inch': ('in3', 'cubic inches'),
    'barrel': ('bbl', 'stb'),
    'reservoir barrel': ('rb',),
    'standard barrel': ('stb', 'stbo', 'stbw', 'stbl', 'oil barrel'),
    }
dictionary['volume_UPPER_REVERSE'] =  ('kstm3', 'Mstm3')
dictionary['volume_PLURALwS'] = ('liter', 'mililiter', 'centiliter', 'deciliter', 'barrel', 'oil barrel', 'gals', 'UKgallons', 'USgallons', 'oil gallon')
dictionary['volume_OGF'] = ('scf', 'cf', 'ft3', 'stb', 'bbl', 'rb', 'stbo', 'stbw', 'stbl')
# dictionary['volume_oilgas_NAMES'] = ('scf','cf','ft3','stb','bbl','rb','stbo','stbw','stbl')
dictionary['volume_oilgas_UPPER'] =  ('sm3', 'm3', 'rm3', 'ksm3', 'Msm3', 'Gsm3',
                                      'scf', 'cf', 'ft3', 'Mscf', 'MMscf', 'Bscf', 'Tscf', 'Mcf', 'MMcf', 'Bcf', 'Tcf',
                                      'stb', 'bbl', 'rb', 'Mstb', 'MMstb', 'Bstb', 'Tstb', 'Mbbl', 'MMbbl', 'Mrb', 'MMrb')

dictionary['volume_product_NAMES'] = {
    'm3': ('m2*m',),
    'cm3': ('cm2*cm',),
    'ft3': ('ft2*ft',),
    'in3':('in2*in',)
    }

dictionary['pressure'] = []
dictionary['pressure_NAMES_UPPER_REVERSE_SPACES'] = {
    'absolute psi': ('psia', 'lb/in2', 'absolute pound/square inch', 'psi absolute'),
    'absolute bar': ('bara', 'barsa', 'abs bar', 'bar absolute'),
    'atmosphere': ('atm', 'atma'),
    'Pascal': ('Pa', 'Newton/m2'),
    'kPa': ('KPa', 'kilopascal'),
    'hPa': ('hectopascal',),
    'Torr': ('millimeters of mercury',),
    'millimeters of mercury': ('mmHg',),
                                        }
dictionary['pressure_NAMES_UPPER_SPACES'] = {
    'psi gauge': ('psi', 'pound/square inch', 'psig', 'gauge psi'),
    'bar gauge': ('bar', 'barg', 'gauge bar', 'bars'),
    }
dictionary['pressure_SI'] = ('Pa', 'bara', 'bar')


dictionary['weight'] = []
dictionary['weight_NAMES_UPPER_REVERSE_SPACES_PLURALwS'] = {
    'gram': ('g',),
    'kilogram': ('kg', 'kgm', 'Kgm',),
    'milligrams': ('mg',),
    'metric ton': ('Tonne',),
    'g-mol': ('g-moles',),
    'Kg-mol': ('Kg-moles',),
    }
dictionary['weight_UK_NAMES_UPPER_REVERSE_SPACES_PLURALwS'] = {
    'grain': ('gr',),
    'pennyweight': ('pwt', 'dwt'),
    'dram': ('dr', 'dramch'),
    'ounce': ('oz',),
    'pound': ('lb', '#', 'libra'),
    'stone': ('st',),
    'quarter': ('qr', 'qrt'),
    # 'hundredweight' : ('cwt',),
    'short hundredweight': ('US hundredweight', 'UScwt'),
    'long hundredweight': ('UK hundredweight', 'UKcwt', 'cwt'),
    # 'ton' : ('t',),
    'short ton': ('USton',),
    'long ton': ('t', 'UKton', 'ton'),
    }
dictionary['weight_SI'] = ('g', 'g-mol')

dictionary['mass'] = ['kilogram mass']


dictionary['density'] = []
dictionary['density_oilgas'] = {}
dictionary['density_NAMES_UPPER'] = {
    'API': ('DEGREES',),
    'SgO': ('gas-gravity','gas-specific-gravity'),
    'SgW': ('water-gravity',),
    'SgG': ('oil-gravity',),
    }
dictionary['density_NAMES_UPPER_REVERSE'] = {
    'g/cm3': ('g/cc',),
    'kg/m3': ('Kg/m3',),
    'lb/ft3': tuple(),
    'psi/ft': tuple(),
    'kJ/rm3': ('KJ/rm3',),
    'lb/stb': tuple(),
    'psia/ft': ('psi/ft',),
    'bara/m': ('bar/m',),
    }



dictionary['compressibility'] = []
dictionary['compressibility_UPPER_NAMES'] = {
    '1/psi': ('1/psia', 'µsip', 'usip', '1/psig'),
    'µsip': ('usip',),
    '1/bar': ('1/bara', '1/barg')
    }


dictionary['rate'] = []
dictionary['rate_NAMES_UPPER_SPACES_REVERSE'] = {
    'standard barrel per day': ('stb/day',),
    'standard cubic foot per day': ('scf/day', 'cf/day', 'scfd'),
    'standard cubic meter per day': ('sm3/day',),
    'barrel per day': ('bbl/day'),
    'cubic meter per day': ('m3/day',),
    'cubic foot per day': ('ft3/day',),
    'reservoir barrel per day': ('rb/day',),
    'reservoir cubic meter per day': ('rm3/day',),
    }
dictionary['rate_NAMES_UPPER_SPACES_REVERSE'] = {
    'stb/day': ('stbd',),
    'scf/day': ('scfd', 'cf/day',),
    'sm3/day': ('sm3d', 'stm3d', 'stm3/day'),
    'bbl/day': ('bbld',),
    'm3/day': ('m3/d',),
    'ft3/day': ('cf/day',),
    }

dictionary['dataBYTE'] = []
dictionary['dataBYTE_UPPER_PLURALwS_DATA_NAME_REVERSE'] = {'B': ('Byte', 'byte')}
dictionary['dataBIT'] = []
dictionary['dataBIT_UPPER_PLURALwS_DATA'] = ('bit',)

dictionary['viscosity'] = []
dictionary['viscosity_UPPER_NAMES_REVERSE'] = {
    'centipoise': ('cP',),
    'Poise': ('dyne*s/cm2', 'g/cm/s'),
    'Pa*s': ('N*s/m2', 'kg/m/s')
    }

dictionary['permeability'] = []
dictionary['permeability_UPPER_REVERSE'] = ('mD', 'Darcy',)

dictionary['force'] = []
dictionary['force_NAMES_SPACES_RECURSIVE_UPPER_REVERSE'] = {
    'Newton': ('N', 'newton', 'kg*m/s2'),
    'kilogram force': ('kgf', 'kilopondio', 'kilogram'),
    'kilopondio': ('kp',),
    'Dyne': ('dyne', 'dyn', 'g*cm/s2')
    }

dictionary['productivityIndex'] = []
dictionary['productivityIndex_UPPER_NAMES_REVERSE'] = {
    'stb/day/psi': ('STB/DAY/', 'stbd/psi', 'stbd/psia', 'stb/day/psia', 'stb/day-psi', 'stb/day-psia', 'stb/d/psi'),
    'sm3/day/bar': ('SM3/DAY/', 'sm3/d/b', 'sm3d/bar', 'sm3d/bara', 'sm3/day/bara', 'sm3/day-bar', 'sm3/day-bara', 'sm3/day/barsa'),
    'sm3/day/kPa': ('sm3d/kPa', 'sm3d/kPa', 'sm3/day-kPa', 'sm3/d/kPa')
    }

dictionary['pressureGradient'] = []
dictionary['pressureGradient'] = ('psi/ft', 'psia/ft', 'psig/ft', 'psi/m', 'psia/m', 'psig/m', 'bar/m', 'bars/m', 'barsa/m', 'bara/m', 'barg/m')

dictionary['acceleration'] = ('m/s2',)

dictionary['other'] = []
dictionary['other_UPPER_NAMES'] = {
    'sec/day': ('sec/d',),
    's2': ('s*s',)
    }

dictionary['dimensionless'] = []
dictionary['dimensionless_fractions_UPPER_NAMES'] = {'fraction': ('ratio', 'dimensionless', 'unitless', 'None', '')}
dictionary['dimensionless_percentage_NAMES_REVERSE'] = {'percentage': ('%'),}

dictionary['date'] = []

dictionary['date_UPPER_PLURALwS'] = ['date']

dictionary['userUnits'] = []
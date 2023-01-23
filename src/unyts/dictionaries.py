#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:14:51 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.12'
__release__ = 20230123
__all__ = ['dictionary', 'SI', 'OGF', 'DATA', 'StandardAirDensity', 'StandardEarthGravity', 'unitless_names']

from json import load as json_load
from pickle import load as pickle_load, dump as pickle_dump
from os.path import isfile
from .parameters import unyts_parameters_, dir_path

StandardAirDensity = 1.225  # Kg/m3 or g/cc
StandardEarthGravity = 9.80665  # m/s2 or 980.665 cm/s2 from

# Sistema Internacional
SI = {
    'Y': (lambda X: X * 1E+24, lambda X: X * 1E+48, lambda X: X * 1E+72),  # yotta
    'Z': (lambda X: X * 1E+21, lambda X: X * 1E+42, lambda X: X * 1E+63),  # zetta
    'E': (lambda X: X * 1E+18, lambda X: X * 1E+36, lambda X: X * 1E+54),  # exa
    'P': (lambda X: X * 1E+15, lambda X: X * 1E+30, lambda X: X * 1E+46),  # peta
    'T': (lambda X: X * 1E+12, lambda X: X * 1E+24, lambda X: X * 1E+36),  # tera
    'G': (lambda X: X * 1E+09, lambda X: X * 1E+18, lambda X: X * 1E+27),  # giga
    'M': (lambda X: X * 1E+06, lambda X: X * 1E+12, lambda X: X * 1E+18),  # mega
    'K': (lambda X: X * 1E+03,) * 3,  # with uppercase K is commonly used to express x1000
    'k': (lambda X: X * 1E+03, lambda X: X * 1E+06, lambda X: X * 1E+09),  # kilo
    'h': (lambda X: X * 1E+02, lambda X: X * 1E+04, lambda X: X * 1E+06),  # hecto
    'd': (lambda X: X * 1E-01, lambda X: X * 1E-02, lambda X: X * 1E-03),  # deci
    'c': (lambda X: X * 1E-02, lambda X: X * 1E-04, lambda X: X * 1E-06),  # centi
    'm': (lambda X: X * 1E-03, lambda X: X * 1E-06, lambda X: X * 1E-09),  # mili
    'µ': (lambda X: X * 1E-06, lambda X: X * 1E-12, lambda X: X * 1E-18),  # micro
    'u': (lambda X: X * 1E-06, lambda X: X * 1E-12, lambda X: X * 1E-18),  # micro
    'n': (lambda X: X * 1E-09, lambda X: X * 1E-18, lambda X: X * 1E-27),  # nano
    'p': (lambda X: X * 1E-12, lambda X: X * 1E-24, lambda X: X * 1E-36),  # pico
    'f': (lambda X: X * 1E-15, lambda X: X * 1E-30, lambda X: X * 1E-45),  # femto
    'a': (lambda X: X * 1E-18, lambda X: X * 1E-36, lambda X: X * 1E-54),  # atto
    'z': (lambda X: X * 1E-21, lambda X: X * 1E-42, lambda X: X * 1E-63),  # zepto
    'y': (lambda X: X * 1E-24, lambda X: X * 1E-48, lambda X: X * 1E-72),  # yocto
}

SI_order = (('Length', 'Pressure', 'Weight', 'Mass', 'Time', 'Frequency', 'Power', 'Voltage', 'Current', 'Resistance'),
            ('Area',),
            ('Rate', 'Volume',),)

DATA = {
    'Y': (lambda X: X * 1E+24, lambda X: X * 2 ** 80),  # yotta
    'Z': (lambda X: X * 1E+21, lambda X: X * 2 ** 70),  # zetta
    'E': (lambda X: X * 1E+18, lambda X: X * 2 ** 60),  # exa
    'P': (lambda X: X * 1E+15, lambda X: X * 2 ** 50),  # peta
    'T': (lambda X: X * 1E+12, lambda X: X * 2 ** 40),  # tera
    'G': (lambda X: X * 1E+09, lambda X: X * 2 ** 30),  # giga
    'M': (lambda X: X * 1E+06, lambda X: X * 2 ** 20),  # mega
    'K': (lambda X: X * 1E+03, lambda X: X * 2 ** 10),  # kilo with uppercase K because it is very common
    'k': (lambda X: X * 1E+03, lambda X: X * 2 ** 10),  # kilo
}

DATA_order = (('dataBIT',), ('dataBYTE',))

# Oil & Gas Field Unit System
OGF = {'M': (None, None, lambda X: X * 1E+03),
       'MM': (None, None, lambda X: X * 1E+06),
       'B': (None, None, lambda X: X * 1E+09),
       'T': (None, None, lambda X: X * 1E+12),
       }
OGF_order = (tuple(), tuple, ('Volume', 'Rate',))


def _load_dictionary() -> (dict, dict):
    print('preparing units dictionary...')

    # the dictionary that contains all the units definitions
    dictionary = {}

    dictionary['Time'] = []
    dictionary['Time_NAMES_REVERSE'] = {
        'nanosecond': ('ns',),
        'millisecond': ('ms',),
        'second': ('s', 'sec',),
        'minute': ('min',),
        'hour': ('h', 'hr', 'Wh/W', 'Watt hour/Watt'),
        'day': ('d', 'día', 'días', 'DíA',),
        'week': ('we', 'w', 'WE',),  # 'w' can be confused with 'W' for Watt
        'month': ('mo', 'mes', 'meses',),
        'year': ('y', 'año',),
        'lustrum': tuple(),
        'decade': tuple(),
        'century': ('centuries',),
    }
    dictionary['Time_PLURALwS_UPPER'] = tuple(dictionary['Time_NAMES_REVERSE'].keys()) + ('min', 'año')
    dictionary['Time_UPPER'] = tuple(t for t in dictionary['Time_NAMES_REVERSE']['nanosecond'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['millisecond'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['second'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['hour'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['day'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['hour'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['month'] if len(t) > 1) + \
                               tuple(t for t in dictionary['Time_NAMES_REVERSE']['year'] if len(t) > 1) + \
                               ('centuries',)
    dictionary['Time_SI'] = ('s',)

    # Temperature and related
    dictionary['Temperature'] = ['C', 'K', 'F', 'R']
    dictionary['Temperature_NAMES'] = {
        'Celsius': ('Centigrade', 'C', 'deg c', 'degrees C'),
        'Fahrenheit': ('F', 'deg F', 'degrees F'),
        'Rankine': ('R', 'deg R', 'degrees R'),
        'Kelvin': ('K', 'deg K', 'degrees K')
    }
    dictionary['Temperature_UPPER_LOWER'] = tuple(dictionary['Temperature_NAMES'].keys()) + \
                                            tuple(t
                                                  for key in dictionary['Temperature_NAMES']
                                                  for t in dictionary['Temperature_NAMES'][key] if len(t) > 1)
    dictionary['TemperatureGradient'] = []

    # Volume
    dictionary['Volume'] = []
    dictionary['Volume_SI_UPPER_REVERSE'] = (
        'm3', 'sm3', 'stm3', 'rm3',)  # 'l' # litre is Volume but the Conversion of SI prefixes is linear
    dictionary['Volume_UK_UPPER_LOWER_NAMES_REVERSE'] = {
        'fluid ounce': ('fl oz', 'oz', 'ounce', 'ozUS', 'ounce'),
        'gill': ('gi', 'gillUS', 'giUS', 'USgill'),
        'pint': ('pt', 'pintUS', 'ptUS', 'USpint'),
        'quart': ('qt', 'quartUS', 'qtUS', 'USquart'),
        'gallonUS': ('gal', 'galUS', 'USgal', 'USgallon', 'gallon', 'gallonsUS'),
        'gallonUK': ('imperial gallon', 'galUK', 'UKgal', 'UKgallon', 'gallonsUK'),  # 'gal', 'gallon'
        'fluid ounce UK': ('fl oz UK', 'ozUK', 'ounceUK'),
        'gillUK': ('giUK', 'UKgill'),
        'pintUK': ('ptUK', 'UKpint'),
        'quartUK': ('qtUK', 'UKquart'),
    }
    dictionary['Volume_NAMES_UPPER_REVERSE_SPACES'] = {
        'litre': ('l', 'liter', 'litro'),
        'millilitre': ('ml', 'milliliter', 'cubic centimeter'),
        'centilitre': ('cl', 'centiliter'),
        'decilitre': ('dl', 'deciliter'),
        'cubic meter': ('CM', 'm3'),
        'standard cubic meter': ('scm', 'sm3', 'stm3', 'm3'),
        'cubic centimeter': ('cc', 'cm3', 'standard cubic centimeter'),
        'standard cubic centimeter': ('scc', 'scm3'),
        'reservoir cubic meter': ('rm3',),
        'reservoir cubic centimeter': ('rcc', 'rcm3'),
        'cubic foot': ('cubic feet', 'ft3', 'cf', 'pie cúbico', 'pie cubico', 'pc', 'pies cúbicos', 'pies cubicos'),
        'standard cubic foot': ('scf', 'cf'),
        'cubic inch': ('in3', 'cubic inches'),
        'barrel': ('bbl', 'stb', 'oil barrel'),
        'reservoir barrel': ('rb',),
        'standard barrel': ('stb', 'stbo', 'stbw', 'stbl', 'oil barrel'),
    }
    dictionary['Volume_UPPER'] = ('kstm3', 'Mstm3')
    dictionary['Volume_PLURALwS_UPPER_LOWER'] = tuple(dictionary['Volume_NAMES_UPPER_REVERSE_SPACES'].keys()) + \
                                          tuple(dictionary['Volume_UK_UPPER_LOWER_NAMES_REVERSE'].keys()) + \
                                          ('fl oz', 'oz', 'ounce', 'gallon', 'imperial gallon', 'barrel', 'gal',
                                           'oil barrel', 'oil gallon',
                                           'USgallon', 'UKgallon', 'USounce', 'UKounce',
                                           'cubic centimeter', 'standard cubic centimeter',
                                           'liter', 'milliliter', 'centiliter', 'deciliter')
    dictionary['Volume_OGF'] = ('scf', 'cf', 'ft3', 'stb', 'bbl', 'rb', 'stbo', 'stbw', 'stbl')
    # dictionary['Volume_oilgas_NAMES'] = ('scf','cf','ft3','stb','bbl','rb','stbo','stbw','stbl')
    dictionary['Volume_oilgas_UPPER'] = ('sm3', 'm3', 'rm3', 'ksm3', 'Msm3', 'Gsm3',
                                         'scf', 'cf', 'ft3', 'Mscf', 'MMscf', 'Bscf', 'Tscf', 'Mcf', 'MMcf', 'Bcf',
                                         'Tcf',
                                         'stb', 'bbl', 'rb', 'Mstb', 'MMstb', 'Bstb', 'Tstb', 'Mbbl', 'MMbbl', 'Mrb',
                                         'MMrb')
    dictionary['Volume_product_NAMES'] = {
        'm3': ('m2*m',),
        'cm3': ('cm2*cm',),
        'ft3': ('ft2*ft',),
        'in3': ('in2*in',)
    }

    # Length
    dictionary['Length'] = []
    dictionary['Length_NAMES_UPPER_REVERSE'] = {'meter': ('m', 'meter', 'metro')}
    dictionary['Length_SI'] = ('m', 'l')  # litre is Volume but the Conversion of SI prefixes is linear
    dictionary['Length_UK_NAMES_REVERSE'] = {
        'thou': ('th',),
        'tenth': ('te', '0.1 in'),
        'inch': ('in', '"'),
        'foot': ('feet', 'ft', "'"),
        'yard': ('yd',),
        'chain': ('ch',),
        'rod': ('rd',),
        'furlong': ('fur',),
        'mile': ('mi',),
        'league': ('lea',),
        'nautical mile': ('nmi',),
        'nautical league': ('nlea',),
    }
    dictionary['Length_UK_UPPER'] = tuple(dictionary['Length_UK_NAMES_REVERSE'].keys()) + \
                                    ('feet', 'in', 'ft', 'yd')

    # Area
    dictionary['Area'] = []
    dictionary['Area_NAMES_UPPER_REVERSE'] = {'square meter': ('sq m', 'm2', 'sqmeter', 'm*m', 'm3/m')}
    dictionary['Area_SI'] = ('m2',)
    dictionary['Area_UK_NAMES_UPPER_REVERSE'] = {
        'square mile': ('sq mi', 'mi2', 'sqmile', 'mi*mi'),
        'acre': tuple(),
        'square rod': ('sq rd', 'sqrd', 'rd2', 'rd*rd'),
        'square yard': ('sq yd', 'sqyd', 'yd2', 'yd*yd'),
        'square foot': ('sq ft', 'sqft', 'ft2', 'ft*ft', 'ft3/ft'),
        'square inch': ('sq in', 'sqin', 'in2', 'in*in', 'in3/in')
    }

    # Pressure
    dictionary['Pressure'] = []
    dictionary['Pressure_NAMES_SPACES'] = {
        'Pascal': ('Pa',),
    }
    dictionary['Pressure_NAMES_UPPER_SPACES'] = {
        'absolute psi': ('psia', 'lb/in2', 'absolute pound/square inch', 'psi absolute', 'libras/pulgada cuadrada absoluta', 'lpca'),
        'psi gauge': ('psi', 'pound/square inch', 'psig', 'gauge psi'),
        'absolute bar': ('bara', 'barsa', 'abs bar', 'bar absolute'),
        'bar gauge': ('bar', 'barg', 'gauge bar', 'bars'),
        'atmosphere': ('atm', 'atma'),
        'Pascal': ('Newton/m2',),
        'kPa': ('KPa', 'kilopascal'),
        'hPa': ('hectopascal',),
        'Torr': ('millimeters of mercury',),
        'millimeters of mercury': ('mmHg',),
    }
    dictionary['Pressure_SI'] = ('Pa', 'bara', 'barsa', 'bar', 'barg')

    dictionary['PressureGradient'] = []
    dictionary['PressureGradient'] = ('psi/ft', 'psia/ft', 'psig/ft', 'psi/m', 'psia/m', 'psig/m', 'bar/m', 'bars/m',
                                      'barsa/m', 'bara/m', 'barg/m')

    # Weight
    dictionary['Weight'] = []
    dictionary['Weight_NAMES_UPPER_LOWER_REVERSE'] = {
        'gram': ('g',),
        'kilogram': ('kg',),
        'milligram': ('mg',),
        'metric ton': ('Tonne',),
        'g-mol': ('g-moles',),
        'Kg-mol': ('Kg-moles',),
    }
    dictionary['Weight_UK_NAMES_UPPER_LOWER_REVERSE_SPACES'] = {
        'grain': ('gr',),
        'pennyweight': ('pwt', 'dwt'),
        'dram': ('dr', 'dramch'),
        'ounce': ('oz',),
        'pound': ('lb', '#', 'libra'),
        'stone': ('st',),
        'quarter': ('qr', 'qrt'),
        # 'hundredweight' : ('cwt',),
        'short hundredweight': ('US hundredweight', 'UScwt', 'swtUS'),
        'long hundredweight': ('UK hundredweight', 'UKcwt', 'cwt', 'swtUK'),
        # 'ton' : ('t',),
        'short ton': ('USton', 'tonUS'),
        'long ton': ('t', 'UKton', 'ton', 'tonUK'),
    }
    dictionary['Weight_PLURALwS_UPPER_LOWER'] = tuple(dictionary['Weight_NAMES_UPPER_LOWER_REVERSE'].keys()) + \
                                                tuple(dictionary['Weight_UK_NAMES_UPPER_LOWER_REVERSE_SPACES'].keys()) + \
                                                ('Tonne', 'ton', 'UKton', 'USton')
    dictionary['Weight_SI'] = ('g', 'g-mol')

    # Mass
    dictionary['Mass'] = ['kilogram mass']
    dictionary['Mass_NAMES_UPPER_LOWER'] = {
        'kilogram mass': ('Kgm', 'kilogram mass')
    }

    # Density
    dictionary['Density'] = []
    dictionary['Density_oilgas'] = {}
    dictionary['Density_NAMES_LOWER_UPPER'] = {
        'API': ('degrees',),
        'SgG': ('gas gravity', 'gas specific gravity'),
        'SgW': ('water gravity',),
        'SgO': ('oil gravity',),
    }
    dictionary['Density_NAMES_UPPER_REVERSE'] = {
        'g/cm3': ('g/cc',),
        'kg/m3': ('Kg/m3',),
        'lb/ft3': tuple(),
        'psi/ft': tuple(),
        'kJ/rm3': ('KJ/rm3',),
        'lb/stb': tuple(),
        'psia/ft': ('psi/ft',),
        'bara/m': ('bar/m',),
    }

    # Compressibility
    dictionary['Compressibility'] = []
    dictionary['Compressibility_UPPER_NAMES'] = {
        '1/psi': ('1/psia', 'µsip', 'usip', '1/psig'),
        'µsip': ('usip',),
        '1/bar': ('1/bara', '1/barg')
    }

    # Rate
    dictionary['Rate'] = []
    dictionary['Rate_NAMES_UPPER_SPACES_REVERSE'] = {
        'standard barrel per day': ('stb/day',),
        'standard cubic foot per day': ('scf/day', 'cf/day', 'scfd'),
        'standard cubic meter per day': ('sm3/day',),
        'barrel per day': ('bbl/day',),
        'cubic meter per day': ('m3/day',),
        'cubic foot per day': ('ft3/day',),
        'reservoir barrel per day': ('rb/day',),
        'reservoir cubic meter per day': ('rm3/day',),
    }
    dictionary['Rate_NAMES_UPPER_SPACES_REVERSE'] = {
        'stb/day': ('stbd',),
        'scf/day': ('scfd', 'cf/day',),
        'sm3/day': ('sm3d', 'stm3d', 'stm3/day'),
        'bbl/day': ('bbld',),
        'm3/day': ('m3/d',),
        'ft3/day': ('cf/day',),
    }

    # digital Data
    dictionary['Data'] = []
    dictionary['Data_UPPER_LOWER_PLURALwS_DATA_NAME_REVERSE'] = {'byte': ('B', 'Byte', 'BYTE'),
                                                                 'bit': ('b', 'Bit', 'BIT')}

    # Viscosity
    dictionary['Viscosity'] = []
    dictionary['Viscosity_UPPER_NAMES_REVERSE'] = {
        'centipoise': ('cP',),
        'Poise': ('dyne*s/cm2', 'g/cm/s'),
        'Pa*s': ('N*s/m2', 'kg/m/s')
    }

    # Permeability
    dictionary['Permeability'] = []
    dictionary['Permeability_NAMES'] = {
        'Darcy': ('D',),
        'millidarcy': ('mD',)
    }
    dictionary['Permeability_UPPER_LOWER'] = ('Darcy', 'millidarcy')
    dictionary['Energy_SI'] = ('D',)

    # Force
    dictionary['Force'] = []
    dictionary['Force_NAMES_SPACES_RECURSIVE_UPPER_REVERSE'] = {
        'Newton': ('N', 'newton', 'kg*m/s2'),
        'kilogram force': ('kgf', 'kilopondio',),  # 'kilogram'
        'kilopondio': ('kp',),
        'Dyne': ('dyne', 'dyn', 'g*cm/s2')
    }

    # Energy
    dictionary['Energy'] = []
    dictionary['Energy_UPPER_LOWER_NAMES_REVERSE_SPACES'] = {
        'Joule': ('J', 'Watt second', 'N*m', 'kg*m2/s2', 'Joules'),
        'Kilojoule': ('kJ',),
        'kilowatt hour': ('kWh', 'kW*h', 'kilovatio hora'),
        'British thermal unit': ('BTU', 'british thermal unit'),
        'Watt second': ('Ws', 'Watt*second', 'W*s'),
        'Watt hour': ('Wh', 'Watt*hour', 'W*h'),
        'gram calorie': ('cal', 'calorie', 'Calorie'),
    }
    dictionary['Energy_SI'] = ('Wh', 'Ws',)

    # Power
    dictionary['Power'] = []
    dictionary['Power_UPPER_NAMES_REVERSE'] = {
        'Horsepower': ('hp',),
        'Watt': ('W', 'J/s', 'VA', 'Volt*Ampere', 'Watt hour/hour', 'V*A', 'Wh/h'),
    }
    dictionary['Power_SI'] = ('W',)

    # Voltage
    dictionary['Voltage'] = []
    dictionary['Voltage_UPPER_NAMES_REVERSE'] = {
        'Volt': ('V', 'Voltio', 'Ampere*Ohm', 'Watt/Ampere', 'A*ohm', 'ohm*A', 'Ohm*Ampere', 'W/A'),
    }
    dictionary['Voltage_SI'] = ('V',)

    # Current
    dictionary['Current'] = []
    dictionary['Current_UPPER_NAMES_REVERSE'] = {
        'Ampere': ('A', 'Watt/Volt', 'Volt/Ohm', 'W/V', 'V/ohm'),
    }
    dictionary['Current_SI'] = ('A',)

    # Resistance
    dictionary['Resistance'] = []
    dictionary['Resistance_UPPER_NAMES_REVERSE'] = {
        'Ohm': ('ohm', 'Ω', 'Volt/Ampere', 'V/A'),
    }
    dictionary['Resistance_SI'] = ('Ω',)

    # Impedance
    dictionary['Impedance'] = []
    dictionary['Impedance_UPPER_NAMES_REVERSE'] = {
        'Ohm': ('ohm', 'Ω',),
    }
    dictionary['Impedance_SI'] = ('Ω',)

    # Conductance
    dictionary['Conductance'] = []
    dictionary['Conductance_UPPER_NAMES_REVERSE'] = {
        'Siemen': ('G', '℧',),
    }
    dictionary['Conductance_SI'] = ('℧',)

    # Capacitance
    dictionary['Capacitance'] = []
    dictionary['Capacitance_UPPER_NAMES_REVERSE'] = {
        'Farad': ('F', 'Faradio', 'Farads', 'farads', 'Coulomb/Volt', 'Q/V'),
    }
    dictionary['Capacitance_SI'] = ('F',)

    # Charge
    dictionary['Charge'] = []
    dictionary['Charge_UPPER_NAMES_REVERSE'] = {
        'Coulomb': ('Q', 'Volt*Farad', 'V*F'),
    }
    dictionary['Charge_SI'] = ('Q',)

    # Inductance
    dictionary['Inductance'] = []
    dictionary['Inductance_UPPER_NAMES_REVERSE'] = {
        'Henry': ('L', 'H'),
    }
    dictionary['Inductance_SI'] = ('H',)

    # Frequency
    dictionary['Frequency'] = []
    dictionary['Frequency_UPPER_NAMES_REVERSE'] = {
        'Hertz': ('Hz', 'hertz', '1/s', 's-1'),
        'RPM': ('rpm', '1/min')
    }
    dictionary['Frequency_SI'] = ('H',)

    # productivity index
    dictionary['ProductivityIndex'] = []
    dictionary['ProductivityIndex_UPPER_NAMES_REVERSE'] = {
        'stb/day/psi': (
            'STB/DAY/', 'stbd/psi', 'stbd/psia', 'stb/day/psia', 'stb/day-psi', 'STB/DAY-PSI', 'stb/day-psia',
            'STB/DAY-PSIA',
            'stb/d/psi'),
        'sm3/day/bar': (
            'SM3/DAY/', 'sm3/d/b', 'sm3d/bar', 'sm3d/bara', 'sm3/day/bara', 'sm3/day-bar', 'SM3/DAY-BAR',
            'sm3/day-bara',
            'SM3/DAY-BARA', 'sm3/day/barsa'),
        'sm3/day/kPa': ('sm3d/kPa', 'sm3d/kPa', 'sm3/day-kPa', 'SM3/DAY-KPA', 'sm3/d/kPa')
    }

    # acceleration
    dictionary['Acceleration'] = ('m/s2', 'ft/s2',)

    # Dimensionless
    dictionary['Dimensionless'] = []
    dictionary['Dimensionless_fractions_UPPER_NAMES'] = {'fraction': ('ratio', 'dimensionless', 'unitless', 'None', '')}

    dictionary['Percentage'] = []
    dictionary['Percentage_NAMES_REVERSE'] = {'percentage': ('%', 'perc', 'percent', '/100'), }

    # Dates
    dictionary['Date'] = []
    dictionary['Date_UPPER_PLURALwS'] = ('date',)

    dictionary['UserUnits'] = []

    # other
    dictionary['otherUnits'] = []
    dictionary['otherUnits_UPPER_NAMES'] = {
        'sec/day': ('sec/d',),
        's2': ('s*s',)
    }

    temperature_ratio_factors = {'Celsius': 9,
                               'Fahrenheit': 5,
                               'Kelvin': 9,
                               'Rankine': 5,
                               }
    temperature_ratio_conversions = {}
    for t1, c1 in temperature_ratio_factors.items():
        for t1a in ((t1,) + dictionary['Temperature_NAMES'][t1]):
            for t2, c2 in temperature_ratio_factors.items():
                for t2a in ((t2,) + dictionary['Temperature_NAMES'][t2]):
                    temperature_ratio_conversions[(t1a, t2a)] = c1 / c2

    unitless_names = dictionary['Dimensionless'] + dictionary['Percentage']
    for name in [names for names in dictionary if names.startswith('Dimensionless') or names.startswith('Percentage')]:
        if type(dictionary[name]) in (tuple, list):
            unitless_names += list(dictionary[name])
        elif type(dictionary[name]) is dict:
            for key in dictionary[name]:
                unitless_names += [key] + list(dictionary[name][key])
    unitless_names = list(set(unitless_names)) + [None]

    if unyts_parameters_.cache_:
        with open(dir_path + 'units/temperature_ratio_conversions.cache', 'wb') as f:
            pickle_dump(temperature_ratio_conversions, f)
        with open(dir_path + 'units/unitless_names.cache', 'wb') as f:
            pickle_dump(unitless_names, f)

    return dictionary, temperature_ratio_conversions, unitless_names


if not unyts_parameters_.reload_ and \
        isfile(dir_path + 'units/units_dictionary.cache') and \
        isfile(dir_path + 'units/units_network.cache') and \
        isfile(dir_path + 'units/temperature_ratio_conversions.cache') and \
        isfile(dir_path + 'units/unitless_names.cache'):
    try:
        with open(dir_path + 'units/units_dictionary.cache', 'r') as f:
            dictionary = json_load(f)
        with open(dir_path + 'units/temperature_ratio_conversions.cache', 'rb') as f:
            temperatureRatioConversions = pickle_load(f)
        with open(dir_path + 'units/unitless_names.cache', 'rb') as f:
            unitless_names = pickle_load(f)
        print('units dictionary loaded from cache...')
    except:
        unyts_parameters_.reload_ = True
        dictionary, temperatureRatioConversions, unitless_names = _load_dictionary()
else:
    dictionary, temperatureRatioConversions, unitless_names = _load_dictionary()

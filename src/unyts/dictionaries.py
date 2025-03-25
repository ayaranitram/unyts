#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 12:14:51 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.5.52'
__release__ = 20250320
__all__ = ['dictionary', 'SI', 'OGF', 'DATA', 'StandardAirDensity', 'StandardEarthGravity', 'StandardWaterDensity',
           'unitless_names', 'uncertain_names']

import logging
from json import load as json_load
from pickle import load as pickle_load, dump as pickle_dump
from os.path import isfile
from .parameters import unyts_parameters_
from .units.def_prefixes import *

StandardAirDensity = 1.225  # Kg/m3 or g/cc
StandardEarthGravity = 9.80665  # m/s2 or 980.665 cm/s2 from
StandardWaterDensity = 1.00  # g/cm3 because the size of the gram was originally based on the mass of a cubic centimetre of water.
SpeedOfLight = 299792458  # m/s
uncertain_names = ['oz', 'ounce', 'ounces', 'OZ', 'OUNCE', 'OUNCES']

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Sistema Internacional
SI = {
    'Q': (si_Q_1, si_Q_2, si_Q_3),  # quetta
    'R': (si_R_1, si_R_2, si_R_3),  # ronna
    'Y': (si_Y_1, si_Y_2, si_Y_3),  # yotta
    'Z': (si_Z_1, si_Z_2, si_Z_3),  # zetta
    'E': (si_E_1, si_E_2, si_E_3),  # exa
    'P': (si_P_1, si_P_2, si_P_3),  # peta
    'T': (si_T_1, si_T_2, si_T_3),  # tera
    'G': (si_G_1, si_G_2, si_G_3),  # giga
    'M': (si_M_1, si_M_2, si_M_3),  # mega
    'K': (si_k_1,) * 3,  # with uppercase K is commonly used to express x1000
    'k': (si_k_1, si_k_2, si_k_3),  # kilo
    'h': (si_h_1, si_h_2, si_h_3),  # hecto
   'da': (si_da_1, si_da_2, si_da_3),  # deca
    'd': (si_d_1, si_d_2, si_d_3),  # deci
    'c': (si_c_1, si_c_2, si_c_3),  # centi
    'm': (si_m_1, si_m_2, si_m_3),  # mili
    'µ': (si_u_1, si_u_2, si_u_3),  # micro
    'u': (si_u_1, si_u_2, si_u_3),  # micro
    'n': (si_n_1, si_n_2, si_n_3),  # nano
    'p': (si_p_1, si_p_2, si_p_3),  # pico
    'f': (si_f_1, si_f_2, si_f_3),  # femto
    'a': (si_a_1, si_a_2, si_a_3),  # atto
    'z': (si_z_1, si_z_2, si_z_3),  # zepto
    'y': (si_y_1, si_y_2, si_y_3),  # yocto
    'r': (si_r_1, si_r_2, si_r_3),  # ronto
    'q': (si_q_1, si_q_2, si_q_3),  # quecto
}

SI_order = (('Length', 'Pressure', 'Weight', 'Mass', 'Time', 'Frequency', 'Power', 'Voltage', 'Current', 'Resistance',
             'Impedance', 'Conductance', 'Capacitance', 'Charge', 'Inductance', 'Energy', 'Permeability'),
            ('Area',),
            ('Rate', 'Volume',),)

DATA = {
    'Y': (data_bit_Y, data_byte_Y),  # yotta
    'Z': (data_bit_Z, data_byte_Z),  # zetta
    'E': (data_bit_E, data_byte_E),  # exa
    'P': (data_bit_P, data_byte_P),  # peta
    'T': (data_bit_T, data_byte_T),  # tera
    'G': (data_bit_G, data_byte_G),  # giga
    'M': (data_bit_M, data_byte_M),  # mega
    'K': (data_bit_K, data_byte_K),  # kilo with uppercase K because it is very common
    'k': (data_bit_K, data_byte_K),  # kilo
}

DATA_order = (('dataBIT',), ('dataBYTE',))

# Oil & Gas Field Unit System
OGF = {'M': (None, None, ogf_M),
       'MM': (None, None, ogf_MM),
       'B': (None, None, ogf_B),
       'T': (None, None, ogf_T),
       }
OGF_order = (tuple(), tuple, ('Volume', 'Rate',))


def _load_dictionary() -> (dict, dict):
    logging.info('preparing units dictionary...')

    # the dictionary that contains all the units definitions
    dictionary = {}

    dictionary['Time'] = []
    dictionary['Time_NAMES_REVERSE'] = {
        'nanosecond': ('ns',),
        'millisecond': ('ms',),
        'second': ('s', 'ss', 'sec',),
        'minute': ('min',),
        'hour': ('h', 'hh', 'hr', 'Wh/W', 'Watt hour/Watt'),
        'day': ('d', 'día', 'días', 'DíA',),
        'week': ('we', 'w', 'WE',),  # 'w' can be confused with 'W' for Watt
        'month': ('mo', 'mes', 'meses',),
        'year': ('y', 'yy', 'yyyy', 'año',),
        'lustrum': tuple(),
        'decade': tuple(),
        'century': ('centuries',),
    }
    dictionary['Time_PLURALwS_UPPER_REVERSE'] = tuple(dictionary['Time_NAMES_REVERSE'].keys()) + ('min', 'año')
    dictionary['Time_UPPER_REVERSE'] = tuple(t for t in dictionary['Time_NAMES_REVERSE']['nanosecond'] if len(t) > 1) + \
                                       tuple(t for t in dictionary['Time_NAMES_REVERSE']['millisecond'] if len(t) > 1) + \
                                       tuple(t for t in dictionary['Time_NAMES_REVERSE']['second'] if len(t) > 1) + \
                                       ('s',) + \
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
        'Celsius': ('Centigrade', 'C', 'deg C', 'degC', 'degrees C',),
        'Fahrenheit': ('F', 'deg F', 'degF', 'degrees F'),
        'Rankine': ('R', 'deg R', 'degR', 'degrees R'),
        'Kelvin': ('K', 'deg K', 'degK', 'degrees K')
    }
    dictionary['Temperature_UPPER_LOWER'] = tuple(dictionary['Temperature_NAMES'].keys()) + \
                                            tuple(t
                                                  for key in dictionary['Temperature_NAMES']
                                                  for t in dictionary['Temperature_NAMES'][key] if len(t) > 1)
    dictionary['TemperatureGradient'] = []

    # Volume
    dictionary['Volume'] = []
    dictionary['Volume_SI_UPPER'] = ('m3', 'm³', 'm^3')  # 'l', 'sm3', 'rm3' are Volume but the conversion of SI prefixes is linear
    dictionary['Volume_linearSI'] = ('sm3', 'sm³', 'Sm3', 'Sm³', 'sm^3',
                                     'stm3', 'stm³', 'STm3', 'STm³', 'stm^3',
                                     'rem3', 'rem³', 'rem^3', 'l')  # litre, sm3 and rem3 are Volume but the conversion of SI prefixes is linear
    dictionary['Volume_UK_NAMES_REVERSE'] = {
        'fluid ounce': ('fl oz', 'oz', 'ounce', 'ozUS'),
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
    dictionary['Volume_NAMES_SPACES_REVERSE'] = {
        'litre': ('l', 'liter', 'litro'),
        'millilitre': ('ml', 'milliliter', 'cubic centimeter'),
        'centilitre': ('cl', 'centiliter'),
        'decilitre': ('dl', 'deciliter'),
        'cubic meter': ('meter3', 'meter^3', 'CM', 'm3', 'm³', 'm^3'),
        'standard cubic meter': ('scm', 'sm3', 'stm3', 'm3', 'Sm3', 'sm³', 'sm^3'),
        'cubic centimeter': ('centimeter3', 'centimeter^3', 'cc', 'cm3', 'standard cubic centimeter', 'cm³', 'cm^3'),
        'standard cubic centimeter': ('scc', 'scm3', 'scm³', 'scm^3'),
        'reservoir cubic meter': ('rem3', 'REm3', 'Rem3', 'rem³', 'rem^3'),
        'reservoir cubic centimeter': ('recc', 'recm3', 'recm³', 'recm^3'),
        'cubic thou': ('thou3', 'thou^3', 'th3', 'th2*th', 'th*th2', 'th³', 'th^3', 'th^2*th', 'th*th^2'),
        'cubic tenth': ('tenth3', 'tenth^3', 'te3', 'te2*te', 'te*te2', 'te³', 'te^3', 'te^2*te', 'te*te^2'),
        'cubic inch': ('cubic inches', 'inche3', 'inche^3', 'in3', 'in2*in', 'in*in2', 'in³', 'in^3', 'in^2*in', 'in*in^2'),
        'cubic foot': ('cubic feet', 'foot3', 'foot^3', 'feet3', 'feet^3', 'ft3', 'ft³', 'cf', 'ft2*ft', 'ft*ft2', 'ft^3', 'ft^2*ft', 'ft*ft^2',
                       'pie cúbico', 'pie cubico', 'pc', 'pies cúbicos', 'pies cubicos'),
        'cubic yard': ('yard3', 'yard^3', 'yd3', 'yd³', 'yd2*yd' 'yd*yd2', 'yd^3', 'yd^2*yd', 'yd*yd^2'),
        'cubic chain': ('chain3', 'chain^3', 'ch3', 'ch³', 'ch2*ch', 'ch*ch2', 'ch^3', 'ch^2*ch', 'ch*ch^2'),
        'cubic rod': ('rod3', 'rod^3', 'rd3', 'rd³', 'rd2*rd', 'rd*rd2', 'rd^3', 'rd^2*rd', 'rd*rd^2'),
        'cubic furlong': ('furlong3', 'furlong^3', 'fur3', 'fur³', 'fur2*fur', 'fur*fur2', 'fur^3', 'fur^2*fur', 'fur*fur^2'),
        'cubic mile': ('mile3', 'mile^3', 'mi3', 'mi³', 'mi2*mi', 'mi*mi2', 'mi^3', 'mi^2*mi', 'mi*mi^2'),
        'cubic league': ('league3', 'league^3', 'lea3', 'lea³', 'lea2*lea', 'lea*lea2', 'lea^3', 'lea^2*lea', 'lea*lea^2'),
        'standard cubic foot': ('scf', 'cf'),
        'barrel': ('bbl', 'stb', 'oil barrel'),
        'reservoir barrel': ('rb', 'reb'),
        'standard barrel': ('stb', 'stbo', 'stbw', 'stbl', 'oil barrel'),
    }
    dictionary['Volume_UPPER'] = ('sm3', 'sm³', 'sm^3', 'stm3', 'stm³', 'stm^3', 'rem3', 'rem³', 'rem^3',
                                  'kstm3', 'kstm³', 'kstm^3', 'Mstm3', 'Mstm³', 'Mstm^3')
    dictionary['Volume_PLURALwS_UPPER_LOWER'] = tuple(dictionary['Volume_NAMES_SPACES_REVERSE'].keys()) + \
                                                tuple(dictionary['Volume_UK_NAMES_REVERSE'].keys()) + \
                                                ('fl oz', 'oz', 'ounce', 'gallon', 'imperial gallon', 'barrel', 'gal',
                                                 'oil barrel', 'oil gallon',
                                                 'USgallon', 'UKgallon', 'USounce', 'UKounce',
                                                 'cubic centimeter', 'standard cubic centimeter',
                                                 'liter', 'milliliter', 'centiliter', 'deciliter')
    dictionary['Volume_OGF'] = ('scf', 'cf', 'ft3', 'ft³', 'ft^3', 'stb', 'bbl', 'rb', 'reb', 'stbo', 'stbw', 'stbl')
    # dictionary['Volume_oilgas_NAMES'] = ('scf','cf','ft3','stb','bbl','rb','stbo','stbw','stbl')
    dictionary['Volume_oilgas_UPPER'] = ('sm3', 'Sm3', 'stm3', 'STm3', 'm3', 'rem3', 'REm3', 'ksm3', 'Msm3', 'Gsm3',
                                         'sm³', 'Sm³', 'stm³', 'STm³', 'm³', 'rem³', 'REm³', 'ksm³', 'Msm³', 'Gsm³',
                                         'sm^3', 'Sm^3', 'stm^3', 'STm^3', 'm^3', 'rem^3', 'REm^3', 'ksm^3', 'Msm^3', 'Gsm^3',
                                         'scf', 'cf', 'ft3', 'Mscf', 'MMscf', 'Bscf', 'Tscf', 'Mcf', 'MMcf', 'Bcf',
                                         'Tcf',
                                         'stb', 'bbl', 'rb', 'reb', 'Mstb', 'MMstb', 'Bstb', 'Tstb', 'Mbbl', 'MMbbl', 'Mrb',
                                         'MMrb')
    dictionary['Volume_product_NAMES_REVERSE'] = {
        'm3': ('m³', 'm^3', 'm2*m', 'm*m2', 'm²*m', 'm*m²', 'm^2*m', 'm*m^2'),
        'cm3': ('cm³', 'cm^3', 'cm2*cm', 'cm*cm2', 'cm²*cm', 'cm*cm²', 'cm^2*cm', 'cm*cm^2'),
        'yd3': ('yd³', 'yd^3', 'yd2*yd', 'yd*yd2', 'yd²*yd', 'yd*yd²', 'yd^2*yd', 'yd*yd^2'),
        'ft3': ('ft³', 'ft^3', 'ft2*ft', 'ft*ft2', 'ft²ft', 'ft*ft²', 'ft^2*ft', 'ft*ft^2'),
        'in3': ('in³', 'in^3', 'in2*in', 'in*in2', 'in²*in', 'in*in²', 'in^2*in', 'in*in^2'),
    }

    # Length
    dictionary['Length'] = []
    dictionary['Length_NAMES_REVERSE_UPPER'] = {'meter': ('m', 'metre', 'metro'),
                                                'parsec': tuple(),  # ('pc',),  "pc" is used also for "pie cúbico"
                                                'astronomical unit': ('au',),
                                                'light year': ('ly', 'lyr')}
    dictionary['Length_SI'] = ('m',)
    dictionary['Length_UK_NAMES_REVERSE'] = {
        'thou': ('th',),
        'tenth': ('te', '0.1 in', '0.1in', '.1in'),
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
                                    ('feet', 'in', 'ft', '0.1 in', '0.1in', '.1in')  # 'yd' uppercase is confused with yottaDarcy

    # Area
    dictionary['Area'] = []
    dictionary['Area_NAMES_REVERSE_UPPER'] = {'square centimeter': ('square centimetre', 'sq cm', 'sqcm',
                                                                    'cm2', 'cm²', 'cm^2',
                                                                    'sqcentimeter', 'cm*cm', 'cm3/cm', 'cm^3/cm'),
                                              'square meter': ('square metre', 'centiare', 'sq m', 'sqm',
                                                               'm2', 'm²', 'm^2',
                                                               'sqmeter', 'm*m', 'm3/m', 'm^3/m'),
                                              'square decameter': ('square decametre', 'are', 'sq dam', 'sqdam',
                                                                   'dam2', 'dam²', 'dam^2',
                                                                   'sqdecameter', 'dam*dam' 'dam3/dam', 'dam^3/dam',
                                              'dam3/dam'),
                                              'square hectometer': ('square hectometre', 'hectare', 'sq hm', 'sqhm',
                                                                    'hm2', 'hm²', 'hm^2',
                                                                    'sqhectometer', 'hm*hm', 'hm3/hm', 'hm^3/hm'),
                                              'square kilometer': ('square kilometre', 'sqkm', 'sq km',
                                                                   'km2', 'km²', 'km^2', 'km*km', 'km3/km', 'km^3/km')}
    dictionary['Area_SI'] = ('m2', 'm²', 'm^2')
    dictionary['Area_UK_NAMES_REVERSE_UPPER'] = {
        'acre': tuple(),
        'square thou': ('thou2', 'thou^2', 'sq th', 'sqth',
                        'th2', 'th²', 'th^2', 'th*th', 'th3/th', 'th³/th', 'th^3/th'),
        'square tenth': ('tenth2', 'tenth^2', 'sq te', 'sqte',
                         'te2', 'te²', 'te^2', 'te*te', 'te3/te', 'te³/te', 'te^3/te'),
        'square inch': ('inch2', 'inch^2', 'sq in', 'sqin',
                        'in2', 'in²', 'in^2', 'in*in', 'in3/in', 'in³/in', 'in^3/in'),
        'square foot': ('foot2', 'foot^2', 'feet2', 'feet^2', 'sq ft', 'sqft',
                        'ft2', 'ft²', 'ft^2', 'ft*ft', 'ft3/ft', 'ft³/ft', 'ft^3/ft'),
        'square yard': ('yard2', 'yard^2', 'sq yd', 'sqyd', 
                        'yd2', 'yd²', 'yd^2', 'yd*yd', 'yd3/yd', 'yd³/yd', 'yd^3/yd'),
        'square chain': ('chain2', 'chain^2', 'sq ch', 'sqch',
                         'ch2', 'ch²', 'ch^2', 'ch*ch', 'ch3/ch', 'ch³/ch', 'ch^3/ch'),
        'square rod': ('rod2', 'rod^2', 'sq rd', 'sqrd',
                       'rd2', 'rd²', 'rd^2', 'rd*rd', 'rd3/rd', 'rd³/rd', 'rd^3/rd'),
        'square furlong': ('furlong2', 'furlong^2', 'sq fur', 'sqfur',
                           'fur2', 'fur²', 'fur^2', 'fur*fur', 'fur3/fur', 'fur³/fur', 'fur^3/fur'),
        'square mile': ('mile2', 'mile^2', 'sq mi', 'mi2', 'mi²', 'mi^2', 'sqmile',
                        'mi*mi', 'mi3/mi', 'mi³/mi', 'mi^3/mi'),
        'square league': ('league2', 'league^2', 'sq lea', 'sqlea',
                          'lea2', 'lea²', 'lea^2', 'lea*lea', 'lea3/lea', 'lea³/lea', 'lea^3/lea'),
    }

    # Pressure
    dictionary['Pressure'] = []
    dictionary['Pressure_NAMES_REVERSE'] = {
        'Pascal': ('Pa',),
    }
    dictionary['Pressure_NAMES_REVERSE_UPPER_SPACES'] = {
        'absolute psi': ('psia', 'lb/in2', 'lb/in²', 'lb/in^2', 'absolute pound/square inch', 'psi absolute',
                         'lpca', 'libras/pulgada cuadrada absoluta'),
        'psi gauge': ('psi', 'pound/square inch', 'psig', 'gauge psi', 'lpc', 'lpcm', 'libras/pulgada cuadrada'),
        'absolute bar': ('bara', 'barsa', 'abs bar', 'bar absolute'),
        'bar gauge': ('bar', 'barg', 'gauge bar', 'bars', 'barsg'),
        'atmosphere': ('atm', 'atma'),
        'Pascal': ('Newton/m2', 'Newton/m²', 'Newton/m^2'),
        'kPa': ('KPa', 'kilopascal', 'kpa'),
        'hPa': ('hectopascal',),
        'Torr': ('millimeters of mercury',),
        'millimeters of mercury': ('mmHg',),
        'kilogram/square centimeter' : ('kg/cm2', 'Kg/cm2', 'kg/cm²', 'kg/cm²', 'kg/cm^2')
    }
    dictionary['Pressure_SI'] = ('Pa', 'bara', 'barsa', 'bar', 'barg')

    dictionary['PressureGradient'] = []
    dictionary['PressureGradient'] = ['psi/ft', 'psi/m', 'bar/m', 'bar/ft']
    dictionary['PressureGradient_NAMES_REVERSE'] = {
        'psi/ft': ('psia/ft', 'psig/ft'),
        'psi/m': ('psia/m', 'psig/m'),
        'bar/m': ('bars/m', 'barsa/m', 'bara/m', 'barsg/m', 'barg/m'),
        'bar/ft': ('bars/ft', 'barsa/ft', 'bara/ft', 'barsg/ft', 'barg/ft')
    }

    # Weight
    dictionary['Weight'] = []
    dictionary['Weight_NAMES_REVERSE'] = {
        'gram': ('g',),
        'kilogram': ('kg',),
        'milligram': ('mg',),
        'microgram': ('ug', 'µg'),
        'metric ton': ('Tonne',),
        'g-mol': ('g-moles',),
        'Kg-mol': ('Kg-moles',),
    }
    dictionary['Weight_UK_NAMES_REVERSE'] = {
        'grain': ('gr',),
        'pennyweight': ('pwt', 'dwt'),
        'dram': ('dr', 'dramch'),
        'ounce': ('oz', 'wt oz', 'weight ounce'),
        'pound': ('lb', '#', 'libra',),
        'stone': ('st',),
        'quarter': ('qr', 'qrt'),
        # 'hundredweight' : ('cwt',),
        'short hundredweight': ('US hundredweight', 'UScwt', 'swtUS'),
        'long hundredweight': ('UK hundredweight', 'UKcwt', 'cwt', 'swtUK'),
        # 'ton' : ('t',),
        'short ton': ('USton', 'tonUS'),
        'long ton': ('t', 'UKton', 'ton', 'tonUK', 'Ton'),
    }
    dictionary['Weight_PLURALwS_UPPER_LOWER_SPACES'] = tuple(dictionary['Weight_NAMES_REVERSE'].keys()) + \
                                                       tuple(dictionary['Weight_UK_NAMES_REVERSE'].keys()) + \
                                                       ('Tonne', 'ton', 'UKton', 'USton', 'lb', 'libra')
    dictionary['Weight_SI'] = ('g', 'g-mol')

    # Mass
    dictionary['Mass'] = ['kilogram mass']
    dictionary['Mass_NAMES_REVERSE_UPPER_LOWER'] = {
        'kilogram mass': ('Kgm', 'kilogram mass')
    }

    # Density
    dictionary['Density'] = []
    dictionary['Density_oilgas'] = {}
    dictionary['Density_NAMES_REVERSE_LOWER_UPPER'] = {
        'API': ('degrees',),
        'SgG': ('gas gravity', 'gas specific gravity', 'sgg'),
        'SgW': ('water gravity', 'sgw'),
        'SgO': ('oil gravity', 'sgo'),
    }
    dictionary['Density_NAMES_REVERSE_UPPER'] = {
        'g/cm3': ('g/cc', 'g/cm³', 'g/cm^3'),
        'kg/m3': ('Kg/m3', 'kg/m³', 'kg/m^3'),
        'lb/ft3': tuple(),
        'lb/yd3': tuple(),
        'psi/ft': tuple(),
        'kJ/rem3': ('KJ/rem3', 'kJ/rem³', 'kJ/rem^3'),
        'kJ/sm3': ('KJ/sm3', 'kJ/sm³', 'KJ/stm3', 'kJ/stm³', 'KJ/stm^3'),
        'kJ/m3': ('KJ/m3', 'kJ/m³', 'KJ/m^3'),
        'lb/stb': tuple(),
        'psia/ft': ('psi/ft', 'psig/ft'),
        'bara/m': ('bar/m', 'barg/m'),
    }

    # Compressibility
    dictionary['Compressibility'] = []
    dictionary['Compressibility_UPPER_NAMES_REVERSE'] = {
        '1/psi': ('1/psia', 'µsip', 'usip', '1/psig'),
        'µsip': ('usip',),
        '1/bar': ('1/bara', '1/barg')
    }

    # Rate
    dictionary['Rate'] = []
    dictionary['Rate_NAMES_REVERSE_UPPER_SPACES'] = {
        'litre per minute': ('lpm', 'litre/minute', 'l/min'),
        'standard barrel per day': ('stb/day',),
        'standard cubic foot per day': ('scf/day', 'cf/day', 'scfd'),
        'standard cubic meter per day': ('sm3/day',),
        'barrel per day': ('bbl/day',),
        'cubic meter per day': ('m3/day', 'm^3/day'),
        'cubic foot per day': ('ft3/day', 'ft^3/day'),
        'cubic yard per day': ('yd3/day', 'yd^3/day'),
        'reservoir barrel per day': ('rb/day', 'reb/day'),
        'reservoir cubic meter per day': ('rem3/day', 'rem3/day', 'rem³/day', 'rem^3/day'),
    }
    dictionary['Rate_NAMES_REVERSE_UPPER_SPACES'] = {
        'stb/day': ('stbd',),
        'scf/day': ('scfd', 'cf/day',),
        'sm3/day': ('sm3d', 'stm3d', 'stm3/day', 'sm³/day', 'sm^3/day', 'sm^3d', 'stm^3d', 'stm^3/day'),
        'bbl/day': ('bbld',),
        'm3/day': ('m3/d', 'm³/day', 'm^3/day', 'm^3/d'),
        'ft3/day': ('cf/day', 'ft^3/day'),
    }

    # Velocity
    dictionary['Velocity'] = ['kilometer per hour', 'mile per hour',]
    dictionary['Velocity_NAMES_REVERSE_UPPER_LOWER'] = {
        'kilometer per hour': ('kilometers per hour', 'kph', 'KPH', 'km/hr'),
        'mile per hour': ('miles per hour', 'mph', 'MPH', 'mi/hr'),
    }

    # digital Data
    # dictionary['Data'] = []
    dictionary['dataBYTE'] = []
    dictionary['dataBYTE_NAMES_REVERSE'] = {'byte': ('B', 'Byte', 'BYTE')}
    dictionary['dataBYTE_DATA'] = ('B', 'byte')
    dictionary['dataBIT'] = []
    dictionary['dataBIT_NAMES_REVERSE'] = {'bit': ('b', 'Bit', 'BIT')}
    dictionary['dataBIT_DATA'] = ('b', 'bit')

    # Viscosity
    dictionary['Viscosity'] = []
    dictionary['Viscosity_NAMES_REVERSE_UPPER'] = {
        'centipoise': ('cP',),
        'Poise': ('dyne*s/cm2', 'g/cm/s', 'dyne*s/cm^2'),
        'Pa*s': ('N*s/m2', 'kg/m/s', 'N*s/m^2')
    }

    # Permeability
    dictionary['Permeability'] = []
    dictionary['Permeability_NAMES_REVERSE'] = {
        'Darcy': ('D',),
        'millidarcy': ('mD',)
    }
    dictionary['Permeability_UPPER_LOWER'] = ('Darcy', 'millidarcy')
    dictionary['Permeability_SI'] = ('D',)

    # Force
    dictionary['Force'] = []
    dictionary['Force_NAMES_REVERSE_SPACES_RECURSIVE_UPPER'] = {
        'Newton': ('N', 'newton', 'kg*m/s2', 'kg*m/s^2'),
        'kilogram force': ('kgf', 'kilopondio',),  # 'kilogram'
        'kilopondio': ('kp',),
        'Dyne': ('dyne', 'dyn', 'g*cm/s2', 'g*cm/s^2')
    }

    # Energy
    dictionary['Energy'] = []
    dictionary['Energy_NAMES_REVERSE_SPACES_UPPER_LOWER'] = {
        'Joule': ('J', 'Watt second', 'N*m', 'kg*m2/s2', 'kg*m^2/s^2', 'Joules'),
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
    dictionary['Power_NAMES_REVERSE_UPPER'] = {
        'Horsepower': ('hp',),
        'Watt': ('W', 'J/s', 'VA', 'Volt*Ampere', 'Watt hour/hour', 'V*A', 'Wh/h'),
    }
    dictionary['Power_SI'] = ('W',)

    # Voltage
    dictionary['Voltage'] = []
    dictionary['Voltage_NAMES_REVERSE_UPPER'] = {
        'Volt': ('V', 'Voltio', 'Ampere*Ohm', 'Watt/Ampere', 'A*ohm', 'ohm*A', 'Ohm*Ampere', 'W/A'),
    }
    dictionary['Voltage_SI'] = ('V',)

    # Current
    dictionary['Current'] = []
    dictionary['Current_NAMES_REVERSE_UPPER'] = {
        'Ampere': ('A', 'Watt/Volt', 'Volt/Ohm', 'W/V', 'V/ohm'),
    }
    dictionary['Current_SI'] = ('A',)

    # Resistance
    dictionary['Resistance'] = []
    dictionary['Resistance_NAMES_REVERSE_UPPER'] = {
        'Ohm': ('ohm', 'Ω', 'Volt/Ampere', 'V/A', 'ohm.m'),
    }
    dictionary['Resistance_SI'] = ('Ω',)

    # Impedance
    dictionary['Impedance'] = []
    dictionary['Impedance_NAMES_REVERSE_UPPER'] = {
        'Ohm': ('ohm', 'Ω',),
    }
    dictionary['Impedance_SI'] = ('Ω',)

    # Conductance
    dictionary['Conductance'] = []
    dictionary['Conductance_NAMES_REVERSE'] = {
        'Siemen': ('G', '℧',),
    }
    dictionary['Conductance_SI'] = ('℧',)
    dictionary['Conductance_UPPER'] = ('Siemen',)

    # Capacitance
    dictionary['Capacitance'] = []
    dictionary['Capacitance_NAMES_REVERSE_UPPER'] = {
        'Farad': ('F', 'Faradio', 'Farads', 'farads', 'Coulomb/Volt', 'Q/V'),
    }
    dictionary['Capacitance_SI'] = ('F',)

    # Charge
    dictionary['Charge'] = []
    dictionary['Charge_NAMES_REVERSE_UPPER'] = {
        'Coulomb': ('Q', 'Volt*Farad', 'V*F', 'Farad*Volt', 'F*V'),
    }
    dictionary['Charge_SI'] = ('Q',)

    # Inductance
    dictionary['Inductance'] = []
    dictionary['Inductance_NAMES_REVERSE_UPPER'] = {
        'Henry': ('L', 'H'),
    }
    dictionary['Inductance_SI'] = ('H',)

    # Frequency
    dictionary['Frequency'] = []
    dictionary['Frequency_NAMES_REVERSE_UPPER'] = {
        'Hertz': ('Hz', 'hertz', '1/s', 's-1', 's^-1'),
        'RPM': ('rpm', '1/min', 'min-1', 'min^-1')
    }
    dictionary['Frequency_SI'] = ('Hz',)

    # productivity index
    dictionary['ProductivityIndex'] = []
    dictionary['ProductivityIndex_NAMES_REVERSE_UPPER'] = {
        'stb/day/psi': (
            'STB/DAY/', 'stbd/psi', 'stbd/psia', 'stb/day/psia', 'stb/day-psi', 'STB/DAY-PSI', 'stb/day-psia',
            'STB/DAY-PSIA',
            'stb/d/psi'),
        'sm3/day/bar': (
            'SM3/DAY/', 'sm3/d/b', 'sm3d/bar', 'sm3d/bara', 'sm3/day/bara', 'sm3/day-bar', 'SM3/DAY-BAR',
            'sm3/day-bara',
            'SM3/DAY-BARA', 'sm3/day/barsa'),
        'sm^3/day/bar': (
            'SM^3/DAY/', 'sm^3/d/b', 'sm^3d/bar', 'sm^3d/bara', 'sm^3/day/bara', 'sm^3/day-bar', 'SM^3/DAY-BAR',
            'sm^3/day-bara',
            'SM^3/DAY-BARA', 'sm^3/day/barsa'),
        'sm3/day/kPa': ('sm3d/kPa', 'sm3d/kPa', 'sm3/day-kPa', 'SM3/DAY-KPA', 'sm3/d/kPa'),
        'sm^3/day/kPa': ('sm^3d/kPa', 'sm^3d/kPa', 'sm^3/day-kPa', 'SM^3/DAY-KPA', 'sm^3/d/kPa')
    }

    # acceleration
    dictionary['Acceleration'] = ['m/s2', 'ft/s2', 'm/s^2', 'ft/s^2']

    # Dimensionless
    dictionary['Dimensionless'] = []
    dictionary['Dimensionless_fractions_NAMES_REVERSE_UPPER'] = {
        'fraction': ('ratio', 'dimensionless', 'unitless', 'None', '')}

    dictionary['Percentage'] = []
    dictionary['Percentage_NAMES_REVERSE'] = {'percentage': ('%', 'perc', 'percent', '/100'), }

    # Dates
    dictionary['Date'] = []
    dictionary['Date_NAMES_REVERSE_UPPER_PLURALwS'] = {'date': ('dates', 'Date', 'Dates')}

    dictionary['UserUnits'] = []

    # other
    dictionary['otherUnits'] = []
    dictionary['otherUnits_NAMES_REVERSE_UPPER'] = {
        'sec/day': ('sec/d',),
        's2': ('s*s', 's^2')
    }

    # validate dictionary
    wrong_definitions = {k: v
                         for k, v in dictionary.items()
                         if type(v) is tuple and (
                                 '_NAMES' not in k
                             and '_REVERSE' not in k
                             and '_UPPER' not in k
                             and '_LOWER' not in k
                             and '_PLURALwS' not in k
                             and '_SPACES' not in k
                             and '_RECURSIVE' not in k
                             and '_SI' not in k
                             and '_UK' not in k
                             and '_OGF' not in k)
                         }
    for k, v in wrong_definitions.items():
        msg = f"dictionary key '{k}' has a value defined as tuple but it must be a list!"
        logging.debug(msg)
        dictionary[k] = list(v)

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
        with open(unyts_parameters_.get_user_folder() + 'temperature_ratio_conversions.cache', 'wb') as f:
            pickle_dump(temperature_ratio_conversions, f)
        with open(unyts_parameters_.get_user_folder() + 'unitless_names.cache', 'wb') as f:
            pickle_dump(unitless_names, f)

    return dictionary, temperature_ratio_conversions, unitless_names


if not unyts_parameters_.reload_ and \
        isfile(unyts_parameters_.get_user_folder() + 'units_dictionary.cache') and \
        isfile(unyts_parameters_.get_user_folder() + 'units_network.cache') and \
        isfile(unyts_parameters_.get_user_folder() + 'temperature_ratio_conversions.cache') and \
        isfile(unyts_parameters_.get_user_folder() + 'unitless_names.cache'):

    try:
        with open(unyts_parameters_.get_user_folder() + 'units_dictionary.cache', 'r') as f:
            dictionary = json_load(f)
        with open(unyts_parameters_.get_user_folder() + 'temperature_ratio_conversions.cache', 'rb') as f:
            temperatureRatioConversions = pickle_load(f)
        with open(unyts_parameters_.get_user_folder() + 'unitless_names.cache', 'rb') as f:
            unitless_names = pickle_load(f)
        logging.info('units dictionary loaded from cache...')
    except:
        unyts_parameters_.reload_ = True
        dictionary, temperatureRatioConversions, unitless_names = _load_dictionary()
else:
    dictionary, temperatureRatioConversions, unitless_names = _load_dictionary()


def _all_units():
    return set([each for units in dictionary.values() for each in units])

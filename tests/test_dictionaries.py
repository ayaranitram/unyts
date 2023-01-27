# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 22:34:17 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.dictionaries import dictionary
from unyts import units
from string import ascii_uppercase


def key2name(txt):
    return (''.join([('_' if s in ascii_uppercase else '') + s.lower() for s in txt])).strip('_')


max_check = 10

for key in dictionary:
    if key in ['Impedance', 'Date', 'otherUnits']:
        continue
    print(key)
    if len(dictionary[key]) > max_check:
        to_check = [u for u in dictionary[key] if
                    (u.count('*') <= 1 and u.count('/') == 0) or (u.count('/') <= 1 and u.count('*') == 0)]
    else:
        to_check = dictionary[key]
    for unit in to_check[:max_check]:
        if key in ['Length', 'Rate'] and unit == 'l' or (len(unit) == 2 and unit.endswith('l')) or (
                '/' in unit and len(unit.split('/')[0]) <= 2 and unit.split('/')[0].endswith('l')):
            continue  # litre is defines as length for SI sufixes (linear multiplier)
        if unit.lower() in ['ounce', 'oz', 'ounces'] and key == 'Weight':
            continue  # 'ounce' can be volume or mass. It is always instantiated as Volume but ounce can be converted to mass
        if key == 'Density' and unit in dictionary['PressureGradient']:
            continue  # pressure gradients have density units
        if key == 'Capacitance' and unit == 'F':
            continue  # F for Farad
        rept_units = [k for k in dictionary for u in dictionary[k] if u == unit]
        if len(rept_units) > 1 and (unit not in ['F', 'l', 'ounces', 'OUNCES', 'ounce', 'OUNCE', 'oz', 'Ohm']
                                    or key not in ['PressureGradient', 'Date', 'Impedance']):
            raise ValueError('unit ' + str(unit) + ' repeated in more than one dictionary:\n ' + '\n '.join(rept_units))
        assert units(1, unit).name.lower() == key2name(key)

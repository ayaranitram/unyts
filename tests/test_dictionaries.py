# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 22:34:17 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.dictionaries import dictionary
from unyts import units
from string import ascii_uppercase

def key2name(txt):
    return (''.join([('_' if s in ascii_uppercase else '') +  s.lower() for s in txt])).strip('_')


for key in dictionary:
    if key == 'Impedance':
        continue
    print(key)
    for unit in dictionary[key]:
        if key == 'Length' and unit == 'l' or (len(unit) == 2 and unit.endswith('l')):
            continue  # litre is defines as length for SI sufixes (linear multiplier)
        if unit.lower() in ['ounce', 'oz', 'ounces'] and key == 'Weight':
            continue  # 'ounce' can be volume or mass. It is always instantiated as Volume but ounce can be converted to mass
        if key == 'Density' and unit in dictionary['PressureGradient']:
            continue  # pressure gradients have density units
        assert units(1, unit).name.lower() == key2name(key)

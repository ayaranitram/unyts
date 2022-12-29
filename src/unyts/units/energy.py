#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.7'
__release__ = 20221229
__all__ = ['energy', 'power']

from ..dictionaries import dictionary
from ..unit_class import Unit
from ..helpers.common_classes import unit_or_str, numeric


class energy(Unit):
    classUnits = dictionary['energy']

    def __init__(self, value: numeric, unit: unit_or_str) -> Unit:
        self.name = 'energy'
        self.kind = energy
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class power(Unit):
    classUnits = dictionary['power']

    def __init__(self, value: numeric, unit: unit_or_str) -> Unit:
        self.name = 'power'
        self.kind = power
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

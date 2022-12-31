#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:17:35 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.4.9'
__release__ = 20221231
__all__ = ['Energy', 'Power']

from unyts.dictionaries import dictionary
from unyts.unit_class import Unit
from unyts.helpers.common_classes import unit_or_str, numeric


class Energy(Unit):
    classUnits = dictionary['Energy']

    def __init__(self, value: numeric, unit: unit_or_str) -> Unit:
        self.name = 'energy'
        self.kind = Energy
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)


class Power(Unit):
    classUnits = dictionary['Power']

    def __init__(self, value: numeric, unit: unit_or_str) -> Unit:
        self.name = 'power'
        self.kind = Power
        self.value = self.check_value(value)
        self.unit = self.check_unit(unit)

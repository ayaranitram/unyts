# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 23:57:43 2023

@author: martin
"""

from unyts.units.data import Data

bit = Data(16, 'bit')
assert type(bit) is Data
assert bit.name == 'data'
assert bit.kind is Data
assert bit.value == 16
assert bit.unit == 'bit'

byte = Data(1, 'byte')
assert type(byte) is Data
assert byte.name == 'data'
assert byte.kind is Data
assert byte.value == 1
assert byte.unit == 'byte'

assert bit.to('byte').value == 2

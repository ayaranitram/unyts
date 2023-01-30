"""
Created on Mon Jan  30 08:14:12 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

import unyts
from unyts import Unit
from unyts.units.geometry import Volume
from unyts.units.force import Weight
from unyts.errors import WrongUnitsError

oz = unyts.units(1, 'oz')
assert type(oz) is Unit
oz_vol = oz.to('ml')
assert type(oz_vol) is Volume
oz_wei = oz.to('g')
assert type(oz_wei) is Weight

assert type(oz_vol.to('ml').to('oz')) is Volume
assert type(oz_wei.to('g').to('oz')) is Weight

try:
    oz_vol.to('ml').to('oz').to('g')
    raise WrongUnitsError('oz volume converted to gram')
except WrongUnitsError:
    pass

try:
    oz_wei.to('g').to('oz').to('ml')
    raise WrongUnitsError('oz volume converted to millilitre')
except WrongUnitsError:
    pass

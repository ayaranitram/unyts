"""
Created on Mon Jan  30 08:14:12 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

import pytest
import unyts
from unyts import Unit
from unyts.units.geometry import Volume
from unyts.units.force import Weight
from unyts.errors import WrongUnitsError
from unyts.parameters import unyts_parameters_

# some conversions can be a little slow when pytest is capturing output
# so bump the timeout to avoid spurious failures during collection.
unyts_parameters_.timeout_ = 5


def test_uncertain_units():
    """Ensure that the ambiguous alias ``oz`` behaves as volume or weight."""
    oz = unyts.units(1, 'oz')
    assert type(oz) is Unit

    oz_vol = oz.to('ml')
    assert type(oz_vol) is Volume

    oz_wei = oz.to('g')
    assert type(oz_wei) is Weight

    assert type(oz_vol.to('ml').to('oz')) is Volume
    assert type(oz_wei.to('g').to('oz')) is Weight

    with pytest.raises(WrongUnitsError):
        oz_vol.to('ml').to('oz').to('g')

    with pytest.raises(WrongUnitsError):
        oz_wei.to('g').to('oz').to('ml')

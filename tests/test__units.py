# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts import units, convert
from unyts.dictionaries import dictionary
from unyts.units.unitless import dimensionless, percentage
from unyts.operations import unitProduct, unitDivision
import numpy as np
import pandas as pd

num = 3
array = np.array([1,2,3,4,5])
limit_dict_units = 3


for kind in [k for k in dictionary if k in ['length']]:
    for unit1 in range(len(dictionary[kind][:limit_dict_units])-1):
        print(dictionary[kind][unit1])
        u1 = units(3.0, dictionary[kind][unit1])

        assert str(u1) == (str(u1.value) + '_' + str(u1.unit))
        assert -u1 == (u1 * -1)
        assert bool(u1) is False if u1.kind in (dimensionless, percentage) else True
        assert abs(u1) == u1.kind(abs(u1.value), u1.unit)

        for op in ('+', '-', '*', '/', '%'):
            assert eval('u1 ' + op + ' num') == units(eval('u1.value ' + op + ' num'), u1.unit)
        assert u1 ** 2 == units(u1.value ** 2, unitProduct(u1.unit, u1.unit))

        for unit2 in range(unit1, len(dictionary[kind][:limit_dict_units])):
            u2 = units(3, dictionary[kind][unit2])
            print(u1, '<->', u2)

            assert u1.to(u2) == units(convert(u1.value, u1.unit, u2.unit), u2.unit)

            assert (u1 + u2) == units(u1.value + convert(u2.value, u2.unit, u1.unit), u1.unit)
            assert (u2 + u1) == units(u2.value + convert(u1.value, u1.unit, u2.unit), u2.unit)

            assert (u1 - u2) == units(u1.value - convert(u2.value, u2.unit, u1.unit), u1.unit)
            assert (u2 - u1) == units(u2.value - convert(u1.value, u1.unit, u2.unit), u2.unit)

            assert (u1 * u2) == units(u1.value * convert(u2.value, u2.unit, u1.unit), unitProduct(u1.unit, u2.unit))
            assert (u2 * u1) == units(u2.value * convert(u1.value, u1.unit, u2.unit), unitProduct(u2.unit, u1.unit))

            assert (u1 / u2) == units(u1.value / convert(u2.value, u2.unit, u1.unit), unitDivision(u1.unit, u2.unit))
            assert (u2 / u1) == units(u2.value / convert(u1.value, u1.unit, u2.unit), unitDivision(u2.unit, u1.unit))

            assert (u1 // u2) == units(u1.value // convert(u2.value, u2.unit, u1.unit), unitDivision(u1.unit, u2.unit))
            assert (u2 // u1) == units(u2.value // convert(u1.value, u1.unit, u2.unit), unitDivision(u2.unit, u1.unit))

            assert (u1 < u2) == (u1.value < convert(u2.value, u2.unit, u1.unit))
            assert (u2 < u1) == (u2.value < convert(u1.value, u1.unit, u2.unit))

            assert (u1 <= u2) is (u1.value <= convert(u2.value, u2.unit, u1.unit))
            assert (u2 <= u1) is (u2.value <= convert(u1.value, u1.unit, u2.unit))

            assert (u1 == u2) is (u1.value == convert(u2.value, u2.unit, u1.unit))
            assert (u2 == u1) is (u2.value == convert(u1.value, u1.unit, u2.unit))

            assert (u1 != u2) is (u1.value != convert(u2.value, u2.unit, u1.unit))
            assert (u2 != u1) is (u2.value != convert(u1.value, u1.unit, u2.unit))

            assert (u1 >= u2) is (u1.value >= convert(u2.value, u2.unit, u1.unit))
            assert (u2 >= u1) is (u2.value >= convert(u1.value, u1.unit, u2.unit))

            assert (u1 > u2) is (u1.value > convert(u2.value, u2.unit, u1.unit))
            assert (u2 > u1) is (u2.value > convert(u1.value, u1.unit, u2.unit))


for kind in [k for k in dictionary if k in ['length']]:  # [k for k in dictionary if k not in ['dimensionless', 'percentage']]:
    for unit1 in range(len(dictionary[kind][:limit_dict_units])-1):
        print(dictionary[kind][unit1])
        u1 = units(array, dictionary[kind][unit1])

        assert str(u1) == (str(u1.value) + '_' + str(u1.unit))
        # assert (-u1).equals((u1 * -1))
        # # assert bool(u1) is False if u1.kind in (dimensionless, percentage) else True
        # assert abs(u1) == u1.kind(abs(u1.value), u1.unit)

        # for op in ('+', '-', '*', '/', '%'):
        #     assert eval('u1 ' + op + ' num') == units(eval('u1.value ' + op + ' num'), u1.unit)
        # assert u1 ** 2 == units(u1.value ** 2, unitProduct(u1.unit, u1.unit))

        # for unit2 in range(unit1, len(dictionary[kind][:limit_dict_units])):
        #     u2 = units(3, dictionary[kind][unit1])
        #     print(u1, '<->', u2)

        #     assert u1.to(u2) == convert(u1.value, u1.unit, u2.unit)

        #     assert (u1 + u2) == units(u1.value + convert(u2.value, u2.unit, u1.unit), u1.unit)
        #     assert (u2 + u1) == units(u2.value + convert(u1.value, u1.unit, u2.unit), u2.unit)

        #     assert (u1 - u2) == units(u1.value - convert(u2.value, u2.unit, u1.unit), u1.unit)
        #     assert (u2 - u1) == units(u2.value - convert(u1.value, u1.unit, u2.unit), u2.unit)

        #     assert (u1 * u2) == units(u1.value * convert(u2.value, u2.unit, u1.unit), unitProduct(u1.unit, u2.unit))
        #     assert (u2 * u1) == units(u2.value * convert(u1.value, u1.unit, u2.unit), unitProduct(u2.unit, u1.unit))

        #     assert (u1 / u2) == units(u1.value / convert(u2.value, u2.unit, u1.unit), unitDivision(u1.unit, u2.unit))
        #     assert (u2 / u1) == units(u2.value / convert(u1.value, u1.unit, u2.unit), unitDivision(u2.unit, u1.unit))

        #     assert (u1 // u2) == units(u1.value // convert(u2.value, u2.unit, u1.unit), unitDivision(u1.unit, u2.unit))
        #     assert (u2 // u1) == units(u2.value // convert(u1.value, u1.unit, u2.unit), unitDivision(u2.unit, u1.unit))
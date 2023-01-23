# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:34:21 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts import units, convert
from unyts.dictionaries import dictionary
from unyts.units.unitless import Dimensionless, Percentage
from unyts.operations import unit_product, unit_division
import numpy as np

num = 3
array = np.array([1, 2, 3, 4, 5])
limit_dict_units = 3


for kind in [k for k in dictionary if k in ['Length']]:
    for unit1 in range(len(dictionary[kind][:limit_dict_units])-1):
        if len(dictionary[kind][unit1]) == 2 and dictionary[kind][unit1].endswith('l'):
            continue
        print(dictionary[kind][unit1])
        u0 = units(2.78, dictionary[kind][unit1])
        u1 = units(3.0, dictionary[kind][unit1])

        assert str(u1) == (str(u1.value) + '_' + str(u1.unit))
        assert -u1 == (u1 * -1)
        assert bool(u1) is False if u1.kind in (Dimensionless, Percentage) else True
        assert abs(u1) == u1.kind(abs(u1.value), u1.unit)
        assert round(u0, 0) == u1

        for op in ('+', '-', '*', '/', '%'):
            assert eval('u1 ' + op + ' num') == units(eval('u1.value ' + op + ' num'), u1.unit)
        assert u1 ** 2 == units(u1.value ** 2, unit_product(u1.unit, u1.unit))

        for unit2 in range(unit1, len(dictionary[kind][:limit_dict_units])):
            if len(dictionary[kind][unit2]) == 2 and dictionary[kind][unit2].endswith('l'):
                continue
            u2 = units(3, dictionary[kind][unit2])
            print(u1, '<->', u2)

            assert u1.to(u2) == units(convert(u1.value, u1.unit, u2.unit), u2.unit)

            assert (u1 + u2) == units(u1.value + convert(u2.value, u2.unit, u1.unit), u1.unit)
            assert (u2 + u1) == units(u2.value + convert(u1.value, u1.unit, u2.unit), u2.unit)

            assert (u1 - u2) == units(u1.value - convert(u2.value, u2.unit, u1.unit), u1.unit)
            assert (u2 - u1) == units(u2.value - convert(u1.value, u1.unit, u2.unit), u2.unit)

            assert (u1 * u2) == units(u1.value * convert(u2.value, u2.unit, u1.unit), unit_product(u1.unit, u2.unit))
            assert (u2 * u1) == units(u2.value * convert(u1.value, u1.unit, u2.unit), unit_product(u2.unit, u1.unit))

            assert (u1 / u2) == units(u1.value / convert(u2.value, u2.unit, u1.unit), unit_division(u1.unit, u2.unit))
            assert (u2 / u1) == units(u2.value / convert(u1.value, u1.unit, u2.unit), unit_division(u2.unit, u1.unit))

            assert (u1 // u2) == units(u1.value // convert(u2.value, u2.unit, u1.unit), unit_division(u1.unit, u2.unit))
            assert (u2 // u1) == units(u2.value // convert(u1.value, u1.unit, u2.unit), unit_division(u2.unit, u1.unit))

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


for kind in [k for k in dictionary if k in ['Length']]:  # [k for k in dictionary if k not in ['Dimensionless', 'Percentage']]:
    for unit1 in range(len(dictionary[kind][:limit_dict_units])-1):
        if len(dictionary[kind][unit1]) == 2 and dictionary[kind][unit1].endswith('l'):
            continue
        print(dictionary[kind][unit1])
        u1 = units(array, dictionary[kind][unit1])

        assert str(u1) == (str(u1.value) + '_' + str(u1.unit))
        # assert (-u1).equals((u1 * -1))
        # # assert bool(u1) is False if u1.kind in (Dimensionless, Percentage) else True
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

assert units(6, 'ft') / units(12, 'in') == units(6, 'ft/ft')
assert (units(6, 'ft') / units(12, 'in')).units == 'ft/ft'
assert units(6, 'ft') @ units(12, 'in') == units(0.5, 'ft/in')
assert (units(6, 'ft') @ units(12, 'in')).units == 'ft/in'

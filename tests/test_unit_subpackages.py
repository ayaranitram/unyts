from unyts import units
from unyts.dictionaries import dictionary
import pytest


def test_each_kind_instantiation_and_self_conversion():
    # For each kind, create a Unit from the first available unit string
    for kind, unit_list in dictionary.items():
        # skip metadata entries
        if kind.endswith('_REVERSE') or kind.endswith('_UPPER') or kind.endswith('_SPACES_REVERSE'):
            continue
        if not unit_list:
            continue
        ustr = unit_list[0]
        u = units(1, ustr)
        assert u.unit == ustr
        # also attempt conversion to itself
        u2 = u.convert(ustr)
        assert u2.unit == ustr

    # additionally, pick a couple of cross-kind conversions to ensure conversions work
    # length to length
    a = units(1, 'm')
    b = units(100, 'cm')
    assert a.to('cm').value == pytest.approx(100)

    # temperature specific
    t = units(0, 'C')
    assert t.to('K').value == pytest.approx(273.15)


def test_invalid_unit_instantiation():
    with pytest.raises(Exception):
        units(1, 'not_a_unit')

    # conversion to incompatible
    with pytest.raises(Exception):
        units(1, 'm').convert('kg')

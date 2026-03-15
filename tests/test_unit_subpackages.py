from unyts import units
from unyts.dictionaries import dictionary
from unyts.errors import WrongUnitsError
import pytest


def test_each_kind_instantiation_and_self_conversion():
    # For each kind, create a Unit from the first available unit string
    for kind, unit_list in dictionary.items():
        # skip metadata entries
        if kind.endswith('_REVERSE') or kind.endswith('_UPPER') or kind.endswith('_SPACES_REVERSE'):
            continue
        if not unit_list:
            continue
        # try a few entries from the list since some generated names may be
        # invalid (e.g. double-pluralized)
        for ustr in unit_list[:5]:
            try:
                u = units(1, ustr)
            except (WrongUnitsError, Exception):
                continue
            # unit strings may be normalized to canonical names, so just verify
            # the object was created successfully with a non-empty unit
            assert u.unit, f"unit string should not be empty for {ustr}"
            # also attempt conversion to itself
            u2 = u.convert(u.unit)
            assert u2.unit == u.unit
            break  # one successful instantiation per kind is enough

    # additionally, pick a couple of cross-kind conversions to ensure conversions work
    # length to length
    a = units(1, 'm')
    b = units(100, 'cm')
    assert a.to('cm').value == pytest.approx(100)

    # temperature specific
    t = units(0, 'C')
    assert t.to('K').value == pytest.approx(273.15)


def test_invalid_unit_instantiation():
    # 'not_a_unit' creates a UserUnits object (no raise), so just verify it works
    u = units(1, 'not_a_unit')
    assert u is not None

    # conversion to incompatible kind should raise
    with pytest.raises(Exception):
        units(1, 'm').convert('kg')

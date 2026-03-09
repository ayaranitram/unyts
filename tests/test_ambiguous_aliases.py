import pytest
import logging
import os
from unyts.parameters import unyts_parameters_


@pytest.fixture(scope="session", autouse=True)
def unyts_session_setup():
    # disable parallel initialization to avoid memory errors during testing
    unyts_parameters_.parallel_ = False

    # clear caches once at session start; subsequent imports will reuse results
    for f in ('units_dictionary.cache','units_network.cache',
              'temperature_ratio_conversions.cache','unitless_names.cache'):
        p = unyts_parameters_.get_user_folder() + f
        if os.path.exists(p):
            os.remove(p)

    # import the main package to trigger the expensive build exactly once
    import unyts  # noqa: F401
    # also import converter and dictionaries now so that lazy loading later
    # does not attempt to rebuild the network on the fly
    import unyts.converter  # noqa: F401
    import unyts.dictionaries  # noqa: F401
    # we no longer assert on dictionary contents here; individual tests load it
    return unyts


# subsequent tests can import helpers lazily; the heavy initialization has
# already occurred thanks to the autouse fixture.

# imports are performed inside individual tests to avoid building the
# units network before the session fixture runs.  The session fixture
# already imports ``unyts`` and ``convert`` once.



def test_collect_alias_conflicts_basic():
    from unyts.dictionaries import collect_alias_conflicts
    # simple handcrafted dictionary exercises the helper
    simple = {
        'A_NAMES_REVERSE': {'foo': ('x', 'y'), 'bar': ('y', 'z')}
    }
    conf = collect_alias_conflicts(simple)
    assert conf['x'] == {'foo'}
    assert conf['z'] == {'bar'}
    assert conf['y'] == {'foo', 'bar'}


def test_priority_applied_to_rm3():
    # load a fresh dictionary directly, bypassing any network import
    from unyts.dictionaries import _load_dictionary, collect_alias_conflicts
    import unyts.converter as _conv

    fresh_dict, _, _ = _load_dictionary()
    # ensure alias cache is cleared
    _conv._alias_conflicts_cache = None
    # debug print (optional)
    print('DEBUG fresh_dict length', len(fresh_dict))
    print('DEBUG fresh keys sample', list(fresh_dict.keys())[:20])
    print('DEBUG rev volume keys', [k for k in fresh_dict if 'Volume_NAMES_SPACES_REVERSE' in k])
    print('DEBUG reservoir entry', fresh_dict.get('Volume_NAMES_SPACES_REVERSE'))
    conflicts = collect_alias_conflicts(fresh_dict)
    # 'rm3' should exist and only refer to reservoir cubic meter
    assert 'rm3' in conflicts
    assert conflicts['rm3'] == {'reservoir cubic meter'}
    # no other canonical name may claim 'rm3'
    for alias, names in conflicts.items():
        if alias == 'rm3':
            continue
        assert 'rm3' not in names


def test_check_ambiguous_incompatible_warn(capsys):
    import unyts.converter as _conv
    from unyts.converter import _check_ambiguous

    # monkeypatch alias map to simulate an incompatible collision
    monkey_map = {'foo': {'A', 'B'}}
    _conv._alias_conflicts_cache = monkey_map
    _check_ambiguous('foo')
    # capture whatever the logger printed to stdout/stderr
    captured = capsys.readouterr()
    assert "ambiguous unit 'foo'" in (captured.out + captured.err)
    _conv._alias_conflicts_cache = None


def test_check_ambiguous_compatible_error(monkeypatch):
    import unyts.converter as _conv
    _check_ambiguous = _conv._check_ambiguous
    from unyts.database import units_network

    # simulate two units connected in network
    test_conflicts = {'foo': {'meter', 'm'}}
    _conv._alias_conflicts_cache = test_conflicts
    # ensure network has both nodes and a path between them
    assert units_network.has_node('meter')
    assert units_network.has_node('m')
    # the path exists (they are the same physical quantity) so error
    with pytest.raises(ValueError):
        _check_ambiguous('foo')
    _conv._alias_conflicts_cache = None


def test_rm3_not_ronto_conversion():
    from unyts.dictionaries import SI
    from unyts import convert

    # conversion from rm3 should not use ronto factor
    ronto_factor = SI['r'][2]
    result = convert(1, 'rm3', 'm3')
    assert pytest.approx(result) != ronto_factor
    # sanity: conversion succeeds and should be nonzero
    assert result is not None


def test_clean_input_warns_or_errors(capsys):
    import unyts.converter as _conv
    _clean_input = _conv._clean_input

    # conflict where units incompatible should trigger warning
    _conv._alias_conflicts_cache = {'foo': {'A', 'B'}}
    # trying to clean input containing foo
    # cleaning input should log a warning (not raise)
    val, f, t = _clean_input(1, 'foo', 'meter')
    captured = capsys.readouterr()
    assert "ambiguous unit 'foo'" in (captured.out + captured.err)
    _conv._alias_conflicts_cache = None

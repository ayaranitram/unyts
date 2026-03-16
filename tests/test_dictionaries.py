# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 22:34:17 2023

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""
import logging
import os
import pytest

from unyts.dictionaries import dictionary, uncertain_names, _load_dictionary
from unyts.parameters import unyts_parameters_
from unyts.database import clean_memory
from string import ascii_uppercase

# ensure cache is disabled for this potentially intensive test and start
# with a clean search memory; the autouse fixture in conftest handles most
# cases, but we set it here explicitly to be extra safe.
unyts_parameters_.cache_ = False
clean_memory()
# rebuild dictionary fresh so we aren't affected by earlier network builds
fresh, _, _ = _load_dictionary()
_original_dictionary = {k: list(v) for k, v in fresh.items()}

# note: we delay importing `units` until inside the loop so the network
# isn't constructed until we actually need it (and only per-assertion).


def pytest_configure(config):
    """Limit xdist workers and disable parallel execution."""
    max_workers = min(8, os.cpu_count() or 1)
    config.option.numprocesses = max_workers
    try:
        from unyts.parameters import unyts_parameters_
        unyts_parameters_.parallel_ = False
    except Exception:
        pass


def key2name(txt):
    """Convert CamelCase dictionary keys into snake_case unit class names."""
    return (''.join([('_' if s in ascii_uppercase else '') + s.lower() for s in txt])).strip('_')


known_duplicated_units = ['F', 'l', 'ounces', 'OUNCES', 'ounce', 'OUNCE', 'oz', 'Ohm', 'ohm', 'OHM']
known_duplicated_keys = ['PressureGradient', 'Date', 'Impedance', 'Capacitance']


def test_dictionary_units():
    max_check = 25

    for key in _original_dictionary:
        if '_' in key:
            continue
        if key in ['Impedance', 'Date', 'otherUnits']:
            continue
        if len(_original_dictionary[key]) > max_check:
            to_check = [u for u in _original_dictionary[key] if
                        (u.count('*') <= 1 and u.count('/') == 0) or (u.count('/') <= 1 and u.count('*') == 0)]
        else:
            to_check = _original_dictionary[key]
        for unit in to_check[:max_check]:
            print(key, unit)
            if key in ['Length', 'Rate'] and (len(unit) <= 2 and unit.endswith('l')) or (
                    '/' in unit and len(unit.split('/')[0]) <= 2 and unit.split('/')[0].endswith('l')):
                continue  # litre is defines as length for SI sufixes (linear multiplier)
            if unit.lower() in ['ounce', 'oz', 'ounces'] and key == 'Weight':
                continue  # 'ounce' can be volume or mass. It is always instantiated as Volume but ounce can be converted to mass
            if key == 'Density' and unit in _original_dictionary.get('PressureGradient', []):
                continue  # pressure gradients have density units
            if key == 'Capacitance' and unit == 'F':
                continue  # F for Farad
            if unit not in known_duplicated_units and key not in known_duplicated_keys:
                rept_units = [k for k in _original_dictionary for u in _original_dictionary[k] if u == unit]
            else:
                rept_units = []
            if len(rept_units) > 1:
                logging.warning('unit ' + str(unit) + ' repeated in more than one dictionary:\n ' + '\n '.join(rept_units))
            if unit in uncertain_names:
                from unyts import units
                assert units(1, unit).name.lower() == 'unit'
            else:
                from unyts import units
                assert units(1, unit).name.lower() == key2name(key)


def test_all_units():
    """Verify that _all_units helper returns a populated set."""
    from unyts.dictionaries import _all_units
    allu = _all_units()
    assert isinstance(allu, set)
    assert len(allu) > 0

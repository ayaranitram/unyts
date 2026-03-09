#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 18:24:20 2020

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.10.1'
__release__ = 20260227
__all__ = ['units', 'convert', 'converter', 'convertible', 'Unit', 'is_Unit', 'valid_unit',
           'set_unit', 'set_conversion', 'set_density', 'get_density',
           'save', 'start_gui', 'set_fvf', 'set_algorithm', 'set_parallel', 'set_timeout', 'verbose']

# Only import lightweight modules at startup
from .parameters import unyts_parameters_, print_path, reload, raise_error, cache, set_density, get_density,\
    recursion_limit, verbose, set_algorithm, get_algorithm, set_parallel, get_parallel, set_timeout, get_timeout,\
    set_logging_level
from .helpers.logger import logger

# Import lightweight infrastructure that doesn't trigger database
from .Empty import Empty
from . import network  # lightweight - just graph data structures

# Print version if requested (lightweight)
if unyts_parameters_.show_version_:
    print(f"loaded unyts version {__version__}")
    unyts_parameters_.show_version_ = False
    unyts_parameters_.save_params()

# ========================================================================
# Lazy loading infrastructure - defer heavy modules
# ========================================================================

import importlib

_loaded_modules = {}


def _load_and_get(module_name, attr_name):
    """Helper to lazily load a module and return an attribute."""
    if module_name not in _loaded_modules:
        _loaded_modules[module_name] = importlib.import_module(f'.{module_name}', __name__)
    return getattr(_loaded_modules[module_name], attr_name)


def __getattr__(name):
    """Called when an attribute is not found in this module's namespace."""
    
    # Database attributes - lazy load (triggers network build/cache load)
    if name in ('network_to_frame', 'save_memory', 'load_memory', 'clean_memory', 'set_fvf', 'get_fvf', 'units_network'):
        db_mod = 'database'
        return _load_and_get(db_mod, name)
    
    # Units function - lazy load (uses database)
    if name == 'units':
        return _load_and_get('units.define', 'units')
    
    # Converter functions - lazy load (uses database)
    if name in ('convert', 'convertible'):
        return _load_and_get('converter', name)
    # provide a convenience alias so ``from unyts import converter`` returns a
    # callable function rather than the module object.  Some legacy tests and
    # user code expect this behaviour.
    if name == 'converter':
        return _load_and_get('converter', 'convert')
    
    # Unit class - lazy load (depends on heavy modules)
    if name == 'Unit':
        return _load_and_get('unit_class', 'Unit')
    if name in ('is_Unit', 'valid_unit'):
        return _load_and_get('unit_class', name)
    
    # Custom units - lazy load
    if name in ('set_unit', 'set_conversion'):
        return _load_and_get('units.custom', name)
    
    # GUI - lazy load
    if name == 'start_gui':
        try:
            return _load_and_get('gui', 'start_gui')
        except Exception:
            def start_gui():
                """Placeholder function when GUI fails to load."""
                logger.error("The GUI is not available in this system.")
            return start_gui
    
    # Try unitary module for pre-defined unit aliases (millimeter, meter, etc.)
    try:
        return _load_and_get('unitary', name)
    except AttributeError:
        pass
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """Return list of available attributes."""
    names = set(__all__)
    # Add common unitary aliases
    try:
        from .unitary import Unitary
        names.update(m.name for m in Unitary)
    except Exception:
        pass
    return sorted(names)


def save(path=None) -> None:
    """
    Will save the current state of searches memory to a cache file that will be loaded next time unyts is started.

    Returns
    -------
    None
    """
    from .database import save_memory
    save_memory(path)


def load(path=None) -> None:
    """
    Will load the saved cache searches into current memory of the converter.

    Returns
    -------
    None
    """
    from .database import load_memory
    load_memory(path)

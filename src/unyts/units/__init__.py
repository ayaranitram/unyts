# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 23:42:15 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>

This package exists primarily to group the various unit definitions
and the ``units`` factory function.  Historically users imported the
factory with ``from unyts import units``.  Because a subpackage named
``unyts.units`` also exists, ``from unyts import units`` normally
returns the package object rather than the function.  In order to
preserve the old behaviour we make the package itself callable and
delegate to the real ``units`` function defined in :mod:`.define`.

The module is therefore transformed at import time into a subclass of
:class:`types.ModuleType` that implements ``__call__``.

During lazy-loading optimisation the top‑level package only exports
this subpackage; the actual ``units`` function is only loaded when
needed, so importing ``unyts.units`` is lightweight until the factory
is invoked.
"""

# --------------------------------------------------------------------------------
# Callable package machinery
# --------------------------------------------------------------------------------
import sys
import types

# placeholder for the real units factory; will be loaded lazily
_units_factory = None


def _load_units():
    """Ensure the real ``units`` function is imported and return it."""
    global _units_factory
    if _units_factory is None:
        from .define import units as _u
        _units_factory = _u
    return _units_factory


class CallableModule(types.ModuleType):
    """A module subclass that proxies calls to the units factory."""

    def __call__(self, value, unit=None, name=None):
        return _load_units()(value, unit, name)


# transform the existing module object into a callable module
_current = sys.modules[__name__]
_current.__class__ = CallableModule

# also expose the factory on the module for direct attribute access
try:
    _current.units = _load_units()
except Exception:
    pass

# support ``from unyts.units import units``
__all__ = ['units']

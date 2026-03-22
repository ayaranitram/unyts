# -*- coding: utf-8 -*-
"""Regression tests for Unyts + SimPandas interoperability.

These tests ensure that when a Unyts `Unit` is on the left-hand side of an arithmetic
operation and the right-hand side is a SimPandas-like object (duck-typed), Unyts
delegates to the object's reflected operator (`__radd__`, `__rsub__`, etc.) rather
than treating it as a generic numeric / array-like.
"""

from unyts import units


class DummySimSeries:
    """Duck-typed stand-in for a SimPandas SimSeries."""

    type = 'SimSeries'

    def __init__(self):
        self.calls = []

    def __radd__(self, other):
        self.calls.append(('radd', other))
        return ('radd', other)

    def __rsub__(self, other):
        self.calls.append(('rsub', other))
        return ('rsub', other)

    def __rmul__(self, other):
        self.calls.append(('rmul', other))
        return ('rmul', other)

    def __rtruediv__(self, other):
        self.calls.append(('rtruediv', other))
        return ('rtruediv', other)


def test_unit_delegates_to_reflected_simseries_add():
    u = units(1.0, 'ft')
    s = DummySimSeries()

    result = u + s
    assert result == ('radd', u)
    assert s.calls == [('radd', u)]


def test_unit_delegates_to_reflected_simseries_sub():
    u = units(1.0, 'ft')
    s = DummySimSeries()

    result = u - s
    assert result == ('rsub', u)
    assert s.calls == [('rsub', u)]


def test_unit_delegates_to_reflected_simseries_mul():
    u = units(1.0, 'ft')
    s = DummySimSeries()

    result = u * s
    assert result == ('rmul', u)
    assert s.calls == [('rmul', u)]


def test_unit_delegates_to_reflected_simseries_truediv():
    u = units(1.0, 'ft')
    s = DummySimSeries()

    result = u / s
    assert result == ('rtruediv', u)
    assert s.calls == [('rtruediv', u)]

# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 22:58:51 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

from unyts.helpers.caster import caster, to_number

def test_caster():
    assert caster('1') == 1 and type(caster('1')) is int
    assert caster('1.5') == 1.5 and type(caster('1.5')) is float
    assert caster('-1-1j') == -1-1j and type(caster('1+1j')) is complex

def test_to_number():
    assert to_number('1') == 1 and type(to_number('1')) is int
    assert to_number('-1') == -1 and type(to_number('-1')) is int
    assert to_number('1 000') == 1000 and type(to_number('1 000')) is int
    assert to_number("1'000") == 1000 and type(to_number("1'000")) is int
    assert to_number('1`000`000') == 1000000 and type(to_number('1`000`000')) is int
    assert to_number('1.') == 1.0 and type(to_number('1.')) is float
    assert to_number('1.0') == 1.0 and type(to_number('1.0')) is float
    assert to_number('1,') == 1.0 and type(to_number('1,')) is float
    assert to_number('1,0') == 1.0 and type(to_number('1,0')) is float
    assert to_number('-1.0') == -1.0 and type(to_number('-1.0')) is float
    assert to_number('-1,0') == -1.0 and type(to_number('-1,0')) is float
    assert to_number('1 000.0') == 1000.0 and type(to_number('1 000.0')) is float
    assert to_number("1'000.") == 1000.0 and type(to_number("1'000.")) is float
    assert to_number('1`000`000.1') == 1000000.1 and type(to_number('1`000`000.1')) is float
    assert to_number('-1.234.569,890') == -1234569.890 and type(to_number('-1.234.569,890')) is float
    assert to_number('-1.234,56') == -1234.56 and type(to_number('-1.234,56')) is float
    assert to_number('1+1j') == 1+1j and type(to_number('1+1j')) is complex
    assert to_number("1.1+1.1j") == 1.1+1.1j and type(to_number('1.1+1.1j')) is complex
    assert to_number('1,1+1,1j') == 1.1+1.1j and type(to_number('1,1+1,1j')) is complex
    assert to_number('-1+1j') == -1+1j and type(to_number('-1+1j')) is complex
    assert to_number("-1.1+1.1j") == -1.1+1.1j and type(to_number('-1.1+1.1j')) is complex
    assert to_number('-1,1+1,1j') == -1.1+1.1j and type(to_number('-1,1+1,1j')) is complex
    assert to_number('1-1j') == 1-1j and type(to_number('1-1j')) is complex
    assert to_number("1.1-1.1j") == 1.1-1.1j and type(to_number('1.1-1.1j')) is complex
    assert to_number('1,1-1,1j') == 1.1-1.1j and type(to_number('1,1-1,1j')) is complex
    assert to_number('-1-1j') == -1-1j and type(to_number('1+1j')) is complex
    assert to_number("-1.1-1.1j") == -1.1-1.1j and type(to_number('-1.1-1.1j')) is complex
    assert to_number('-1,1-1,1j') == -1.1-1.1j and type(to_number('-1,1-1,1j')) is complex
    assert to_number('1E2') == 100 and type(to_number('1E2')) is int
    assert to_number('-1E2') == -100 and type(to_number('-1E2')) is int
    assert to_number('1.E2') == 100.0 and type(to_number('1.E2')) is float
    assert to_number('1.1E2') == 110.0 and type(to_number('1.1E2')) is float
    assert to_number('-1.1E2') == -110.0 and type(to_number('-1.1E2')) is float
    assert to_number('1E2+1E1j') == 100+10j and type(to_number('1E2+1E1j')) is complex
    assert to_number('-1E2-1E1j') == -100-10j and type(to_number('-1E2-1E1j')) is complex
    assert to_number('-1,2E2-1,3E1j') == -120-13j and type(to_number('-1,2E2-1,3E1j')) is complex

    for t in (1,-1,1.,1.0,-1.0,1+1j,1-1j,-1+1j,-1-1j):
        assert to_number(t) == t and type(to_number(t)) is type(t)

    # next should raise error
    for t in ('a',' ','1.00,2','1.234.56','1 234 56','1,234,56','1,234,567'):
        try:
            to_number(t)
            raise AssertionError('evaluating to_number in ' + t)
        except ValueError:
            pass
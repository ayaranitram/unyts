# -*- coding: utf-8 -*-
"""
Created on Sun May 23 11:27:57 2021

@author: martin
"""
from units._helpers import isnumber, tonumber

def test_isnumber():
    assert isnumber(1) is True
    assert isnumber(0) is True
    assert isnumber(-1) is True
    assert isnumber(1.0) is True
    assert isnumber(-1.0) is True
    assert isnumber('1') is True
    assert isnumber('-1') is True
    assert isnumber('1.0') is True
    assert isnumber('-1.0') is True
    assert isnumber('1+1j') is True
    assert isnumber('-1+1j') is True
    assert isnumber('-1-1j') is True
    assert isnumber('A') is False
    
def test_tonumber():
    assert tonumber('1') == 1 and type(tonumber('1')) is int
    assert tonumber('-1') == -1 and type(tonumber('-1')) is int
    assert tonumber('1 000') == 1000 and type(tonumber('1 000')) is int
    assert tonumber("1'000") == 1000 and type(tonumber("1'000")) is int
    assert tonumber('1`000`000') == 1000000 and type(tonumber('1`000`000')) is int
    assert tonumber('1.') == 1.0 and type(tonumber('1.')) is float
    assert tonumber('1.0') == 1.0 and type(tonumber('1.0')) is float
    assert tonumber('1,') == 1.0 and type(tonumber('1,')) is float
    assert tonumber('1,0') == 1.0 and type(tonumber('1,0')) is float
    assert tonumber('-1.0') == -1.0 and type(tonumber('-1.0')) is float
    assert tonumber('-1,0') == -1.0 and type(tonumber('-1,0')) is float
    assert tonumber('1 000.0') == 1000.0 and type(tonumber('1 000.0')) is float
    assert tonumber("1'000.") == 1000.0 and type(tonumber("1'000.")) is float
    assert tonumber('1`000`000.1') == 1000000.1 and type(tonumber('1`000`000.1')) is float
    assert tonumber('-1.234.569,890') == -1234569.890 and type(tonumber('-1.234.569,890')) is float
    assert tonumber('-1.234,56') == -1234.56 and type(tonumber('-1.234,56')) is float
    assert tonumber('1+1j') == 1+1j and type(tonumber('1+1j')) is complex
    assert tonumber("1.1+1.1j") == 1.1+1.1j and type(tonumber('1.1+1.1j')) is complex
    assert tonumber('1,1+1,1j') == 1.1+1.1j and type(tonumber('1,1+1,1j')) is complex
    assert tonumber('-1+1j') == -1+1j and type(tonumber('-1+1j')) is complex
    assert tonumber("-1.1+1.1j") == -1.1+1.1j and type(tonumber('-1.1+1.1j')) is complex
    assert tonumber('-1,1+1,1j') == -1.1+1.1j and type(tonumber('-1,1+1,1j')) is complex
    assert tonumber('1-1j') == 1-1j and type(tonumber('1-1j')) is complex
    assert tonumber("1.1-1.1j") == 1.1-1.1j and type(tonumber('1.1-1.1j')) is complex
    assert tonumber('1,1-1,1j') == 1.1-1.1j and type(tonumber('1,1-1,1j')) is complex
    assert tonumber('-1-1j') == -1-1j and type(tonumber('1+1j')) is complex
    assert tonumber("-1.1-1.1j") == -1.1-1.1j and type(tonumber('-1.1-1.1j')) is complex
    assert tonumber('-1,1-1,1j') == -1.1-1.1j and type(tonumber('-1,1-1,1j')) is complex
    assert tonumber('1E2') == 100 and type(tonumber('1E2')) is int
    assert tonumber('-1E2') == -100 and type(tonumber('-1E2')) is int
    assert tonumber('1.E2') == 100.0 and type(tonumber('1.E2')) is float
    assert tonumber('1.1E2') == 110.0 and type(tonumber('1.1E2')) is float
    assert tonumber('-1.1E2') == -110.0 and type(tonumber('-1.1E2')) is float
    assert tonumber('1E2+1E1j') == 100+10j and type(tonumber('1E2+1E1j')) is complex
    assert tonumber('-1E2-1E1j') == -100-10j and type(tonumber('-1E2-1E1j')) is complex
    assert tonumber('-1,2E2-1,3E1j') == -120-13j and type(tonumber('-1,2E2-1,3E1j')) is complex
    
    for t in (1,-1,1.,1.0,-1.0,1+1j,1-1j,-1+1j,-1-1j):
        assert tonumber(t) == t and type(tonumber(t)) is type(t)
    
    # next should raise error
    for t in ('a',' ','1.00,2','1.234.56','1 234 56','1,234,56','1,234,567'):
        try:
            tonumber(t)
            raise AssertionError('evaluating tonumber in ' + t)
        except ValueError:
            pass
        

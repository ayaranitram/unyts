import pytest
from unyts.errors import (WrongUnitsError, WrongValueError, WrongDateFormatError,
                           NoConversionFoundError, NoFVFError, SearchTimeoutError)


def test_error_messages():
    e = WrongUnitsError()
    assert 'ERROR: Wrong Units' in e.message
    e = WrongUnitsError('bad unit')
    assert 'bad unit' in e.message

    e = WrongValueError()
    assert 'ERROR: Wrong Value' in e.message

    e = WrongDateFormatError()
    assert 'ERROR: Wrong Date Format' in e.message

    e = NoConversionFoundError()
    assert 'Conversion path not found' in e.message

    e = NoFVFError()
    assert 'FVF constant not defined' in e.message

    e = SearchTimeoutError()
    assert 'timeout limit' in e.message
    e = SearchTimeoutError(5)
    assert '5 seconds' in e.message
    e = SearchTimeoutError(None)
    assert 'exceeded the timeout limit' in e.message
    e = SearchTimeoutError('custom')
    assert e.message == 'custom'

import pytest
import math
import threading
from unyts.helpers.is_number import is_number
from unyts.helpers.caster import caster, to_number
from unyts.helpers.multi_split import multi_split
from unyts.helpers.unit_string_tools import (split_ratio, split_product, split_unit,
                                              reduce_parentheses, reduce_units)
from unyts.helpers.is_unit import is_unit
from unyts.helpers.logger import UnytLogger, ColorCodes
from unyts.helpers.timer import timeit
from unyts.helpers import _parallel_helpers
from unyts.parameters import unyts_parameters_


def test_is_number():
    assert is_number('123')
    assert is_number('-12.3')
    assert is_number('3+4j')
    assert not is_number('abc')


def test_caster_and_to_number():
    assert caster('10') == 10
    assert caster('3.14') == 3.14
    assert caster('1+2j') == 1+2j
    with pytest.raises(ValueError):
        caster('not a num')

    assert to_number('1,234.56') == 1234.56
    assert to_number('1.234,56') == 1234.56
    assert to_number('(5)') == -5
    assert to_number('1e3') == 1000
    assert to_number(7) == 7
    with pytest.raises(TypeError):
        to_number(None)
    with pytest.raises(ValueError):
        to_number('1.2.3')


def test_multi_split_and_unit_string_tools():
    assert multi_split('a/b*c', sep=('/', '*')) == ['a', '/', 'b', '*', 'c']
    with pytest.raises(TypeError):
        multi_split(123)

    assert split_ratio('m/s') == ['m', 's']
    assert split_product('m*s') == ['m', 's']
    assert split_unit('m/s*kg') == ['m', '/', 's', '*', 'kg']

    assert reduce_parentheses('m/(s)') == 'm/s'
    assert reduce_parentheses('m') == 'm'
    with pytest.raises(ValueError):
        reduce_parentheses('m)')
    with pytest.raises(ValueError):
        reduce_parentheses('(m')

    assert reduce_units('m/m') == 'dimensionless'
    assert reduce_units('m*m') == 'm*m'  # nothing to cancel
    assert reduce_units(None) is None
    with pytest.raises(ValueError):
        reduce_units(None, raise_error=True)
    with pytest.raises(NotImplementedError):
        reduce_units('m+kg', raise_error=True)


def test_is_unit():
    assert is_unit('m')
    assert is_unit('m/s')
    assert not is_unit('notunit')
    with pytest.raises(TypeError):
        is_unit(123)


def test_logger_basic(caplog):
    log = UnytLogger(name='TestLogger', default_level='debug', mode='console')
    assert log.get_current_level() == 'DEBUG'
    assert log.set_level('info') is True
    assert log.get_current_level() == 'INFO'
    assert log.set_level('invalid') is False
    # writing messages should not raise
    caplog.set_level('INFO', logger='TestLogger')
    log.info('hello')
    log.warning('warn')
    log.error('err')
    assert '[Unyts INFO]' in caplog.text or 'hello' in caplog.text

    log.force_console_mode()
    assert log.mode == 'console'
    # forcing jupyter mode may or may not succeed depending on environment; just call
    log.force_jupyter_mode()


def test_timer_decorator(capsys):
    # with timing disabled, decorator returns original function
    unyts_parameters_._timing = False
    @timeit
    def f1(x):
        return x+1
    assert f1(1) == 2
    # enable timing and verify output prints
    unyts_parameters_._timing = True
    @timeit
    def f2(x):
        return x*2
    out = f2(3)
    captured = capsys.readouterr()
    assert 'execution time' in captured.out
    assert out == 6
    unyts_parameters_._timing = False


def test_parallel_execute():
    # successful parallel run
    def a():
        return 1
    def b():
        return 2
    res = _parallel_helpers.parallel_execute([a, b], max_workers=2)
    assert res['a'] == 1 and res['b'] == 2

    # exception propagation
    def fail():
        raise RuntimeError('oops')
    with pytest.raises(RuntimeError):
        _parallel_helpers.parallel_execute([a, fail])

    # timeout triggers exception
    import time
    def slow():
        time.sleep(0.1)
        return 0
    with pytest.raises(Exception):
        _parallel_helpers.parallel_execute([slow, slow], timeout=0.001)

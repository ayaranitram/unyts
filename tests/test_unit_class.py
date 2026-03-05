import pytest
import numpy as np
from unyts import units
from unyts.unit_class import Unit
from unyts.errors import WrongUnitsError, NoConversionFoundError


def test_basic_properties_and_str():
    u = units(5, 'm')
    assert u.value == 5
    assert u.unit == 'm'
    assert str(u) == '5_m'
    assert repr(u) == '5_m'


def test_dtype_and_iteration():
    u = units(5, 'm')
    # dtype on scalar with numpy available
    assert hasattr(u.dtype, 'name')
    # iteration over scalar returns one element
    assert list(iter(u)) == [5]
    # indexing on scalar raises IndexError
    with pytest.raises(IndexError):
        _ = u[1]

    # vector value
    arr = np.array([1,2,3])
    v = units(arr, 'm')
    assert v.dtype == arr.dtype
    assert list(v) == [1,2,3]
    assert v[1].value == 2


def test_round_and_equals():
    u = units(1.2345, 'm')
    assert round(u, 2).value == round(1.2345, 2)
    assert u.equals(units(1.2345, 'm'))
    assert u.equals(1.2345)
    with pytest.raises(TypeError):
        u.equals('abc')
    # precision argument
    assert units(1.234, 'm').equals(units(1.235, 'm'), precision=2) is True


def test_convert_and_to_errors():
    u = units(1, 'm')
    # valid conversion
    v = u.convert('cm')
    assert v.unit == 'cm'
    # invalid type for conversion
    with pytest.raises(TypeError):
        u.convert(123)
    # incompatible units should raise WrongUnitsError or NoConversionFoundError
    with pytest.raises((WrongUnitsError, NoConversionFoundError)):
        units(1, 'm').convert('kg')


def test_boolean_and_abs():
    u = units(0, 'm')
    assert bool(u)
    assert abs(units(-1, 'm')).value == 1


def test_arithmetic_tuple_and_numeric():
    u = units(2, 'm')
    assert (u + 3).value == 5
    assert (u * 3).value == 6
    assert (u - 1).value == 1
    assert (u / 2).value == 1
    assert (u // 2).value == 1
    assert (u ** 2).value == 4
    assert (u @ units(2, 'm')).unit == 'm/m'
    # tuple behaviour
    t = (1, u)
    assert (u + t)[1].value == 3


def test_check_value_behaviors():
    # check_value should convert list to numpy array
    u = units([1,2], 'm')
    assert isinstance(u.value, np.ndarray)

    with pytest.raises(Exception):
        units(object(), 'm')

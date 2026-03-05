from unyts import get_fvf, set_fvf, converter
import pytest


@pytest.fixture(autouse=True)
def default_fvf_fixture():
    """Save and restore FVF around each test."""
    original = get_fvf()
    yield original
    set_fvf(original)


def test_get_and_set_fvf(default_fvf_fixture):
    default_fvf = default_fvf_fixture
    assert isinstance(default_fvf, float) or default_fvf is None, "get_fvf should return a float or None"
    if default_fvf is not None:
        assert default_fvf > 0, "Default FVF should be a positive number"

    set_fvf(2.0)
    assert get_fvf() == 2.0, "get_fvf should return the value set by set_fvf"

    assert converter(1, 'rm3', 'sm3') == pytest.approx(1.0 / get_fvf()), \
        "Conversion from rm3 to sm3 should be 1/FVF"


def test_raise_value_error():
    with pytest.raises(ValueError):
        set_fvf(-1, 'kg/m3')

def test_raise_type_error():
    with pytest.raises(TypeError):
        set_fvf('not a number', 'kg/m3')
from unyts import set_density, get_density, convert
from unyts.units.ratios import Density
import pytest
import math
import unyts.converter as converter_module


@pytest.fixture(autouse=True)
def default_density_fixture():
    """Ensure density is restored after each test."""
    original = get_density()
    yield original
    set_density(original)


def test_get_and_set_density(default_density_fixture):
    # verify default value type and positivity
    default_density = default_density_fixture
    assert isinstance(default_density, Density), "get_density should return a Density object"
    assert default_density > 0, "Default density should be a positive number"

    # set a new density and verify conversion to g/cm3
    set_density(1000, 'kg/m3')
    assert get_density() == 1.0, "get_density should return the value set by set_density converted to g/cm3"

    # confirm the effect on converter between kg and litre
    assert convert(1, 'kg', 'l') == pytest.approx(1.0 / get_density().value), \
        "Conversion from kg to l should be 1/density in g/cm3"

    # changing the density again updates converter behavior
    set_density(2000, 'kg/m3')
    assert convert(1, 'kg', 'l') == pytest.approx(1.0 / get_density().value), \
        "Conversion from kg to l should be 1/density in g/cm3"


def test_raise_value_error():
    with pytest.raises(ValueError):
        set_density('not a number', 'kg/m3')


@pytest.mark.parametrize('bad_density', [0, -1, -0.001, math.nan, math.inf, -math.inf])
def test_set_density_rejects_non_positive_or_non_finite_values(bad_density):
    with pytest.raises(ValueError):
        set_density(bad_density, 'g/cm3')


@pytest.mark.parametrize('high_density', [1e3, 1e6])
def test_set_density_accepts_high_positive_finite_values(high_density):
    set_density(high_density, 'g/cm3')
    d = get_density()
    assert d.value == pytest.approx(high_density)
    # kg -> l uses 1/density relationship in g/cm3 system
    assert convert(1, 'kg', 'l') == pytest.approx(1.0 / high_density)


def test_density_conversion_returns_empty_on_converter_timeout(monkeypatch):
    def _timeout_converter(*args, **kwargs):
        return converter_module.Empty, None

    monkeypatch.setattr(converter_module, '_converter', _timeout_converter)

    conv1, path1 = converter_module._density_conversion(1, 'l', 'kg')
    conv2, path2 = converter_module._density_conversion(1, 'kg', 'l')

    assert conv1 is converter_module.Empty
    assert conv2 is converter_module.Empty
    assert path1 is None
    assert path2 is None
        
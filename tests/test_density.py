from unyts import set_density, get_density, convert
from unyts.units.ratios import Density
import pytest


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
        
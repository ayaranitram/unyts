import pytest
from unyts.unit_class import Unit


def test_unitary_star_import():
    """Verify that 'from unyts.unitary import *' works and produces Unit objects."""
    # Import inside test so failure is captured as a test error, not a
    # collection error.
    from unyts import unitary

    expected = {
        'bit': 'b', 'byte': 'B',
        'millimetre': 'mm', 'meter': 'm', 'inch': 'in', 'foot': 'ft',
        'mile': 'mi', 'yard': 'yd', 'kilometre': 'km',
        'barrel': 'stb', 'litre': 'l', 'sm3': 'sm3',
        'gram': 'g', 'kilogram': 'kg', 'pound': 'lb',
        'second': 'sec', 'minute': 'min', 'hour': 'hour', 'day': 'day',
        'celsius': 'deg C', 'fahrenheit': 'deg F', 'kelvin': 'deg K',
        'pascal': 'Pa', 'psi': 'psia', 'bar': 'barsa',
        'newton': 'N', 'joule': 'J', 'watt': 'W',
        'volt': 'V', 'ampere': 'A', 'hertz': 'Hz',
    }
    for name, expected_unit in expected.items():
        obj = getattr(unitary, name)
        assert isinstance(obj, Unit), f"{name} should be a Unit instance"
        assert obj.unit == expected_unit, f"{name}.unit should be '{expected_unit}', got '{obj.unit}'"
        assert obj.value == 1, f"{name}.value should be 1"
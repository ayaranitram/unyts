"""Public Python API tests for the optional C++ conversion engine."""

import pytest

import unyts


cpp = pytest.importorskip('unyts_cpp_native', reason='optional C++ engine is not built')


@pytest.fixture
def restore_engine():
    original = unyts.get_engine()
    try:
        yield
    finally:
        unyts.set_engine(original)


def test_cpp_engine_converts_safe_scalar_values(restore_engine):
    unyts.set_engine('cpp')

    assert unyts.convert(1, 'km', 'm') == pytest.approx(1000.0)
    assert unyts.convert(1, 'kg', 'lb') == pytest.approx(2.2046226218487757)
    assert unyts.convertible('kg', 'lb') is True


def test_cpp_engine_preserves_python_only_conversion_features(restore_engine):
    unyts.set_engine('cpp')

    conversion = unyts.convert(None, 'km', 'm')
    assert callable(conversion)
    assert conversion(1) == pytest.approx(1000.0)

    python_result = unyts.convert(1, 'PSI', 'bar')
    unyts.set_engine('python')
    assert python_result == pytest.approx(unyts.convert(1, 'PSI', 'bar'))
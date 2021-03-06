import pytest
import pyimplicit_conversion as m

def test_from_class_implicit_without_annotation():
    with pytest.raises(TypeError, match="incompatible function arguments"):
        m.test_value(m.One())

def test_from_class_explicit_without_annotation():
    with pytest.raises(TypeError, match="incompatible function arguments"):
        m.test_value(m.Two())

def test_from_class_implicit_with_annotation():
    assert m.test_value(m.Three()) == 3

def test_from_pod_explicit_without_annotation():
    with pytest.raises(TypeError, match="incompatible function arguments"):
        m.test_value(2.0)

def test_from_pod_implicit_with_annotation():
    assert m.test_value(42) == 42

def test_by_reference():
    number = m.Number(123)
    assert m.test_by_reference(number) == 123

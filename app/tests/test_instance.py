import pytest

from app.services.a_indicators import compA1_1
from app.models.instance import Instance


def test_webpage_empty_strings():
    try:
        instance = Instance(type='rest', webpage=[""])
        assert instance is not None  # Confirm the instance is created
    except Exception as e:
        pytest.fail(f"Instantiation failed with error: {e}")


def test_webpage_ok():
    try:
        instance = Instance(type='rest', webpage=["https://github.com"])
        assert instance is not None  # Confirm the instance is created
    except Exception as e:
        pytest.fail(f"Instantiation failed with error: {e}")


def test_webpage_empty():
    try:
        instance = Instance(type='rest', webpage=[])
        assert instance is not None  # Confirm the instance is created
    except Exception as e:
        pytest.fail(f"Instantiation failed with error: {e}")
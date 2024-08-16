import pytest
from io import StringIO
import logging

from app.services.f_indicators import compF1_2
from app.models.instance import Instance

def test_compF1_2_valid_version():
    instance = Instance(version="1.0.0")
    result, log_output = compF1_2(instance)
    assert result == True

def test_compF1_2_valid_version_x_x():
    instance = Instance(version="1.0")
    result, log_output = compF1_2(instance)
    assert result == True


def test_compF1_2_invalid_version_parts():
    instance = Instance(version="1")
    result, log_output = compF1_2(instance)
    assert result == False

def test_compF1_2_invalid_version_digit():
    instance = Instance(version="1.a")
    result, log_output = compF1_2(instance)
    assert result == False

def test_compF1_2_no_version():
    instance = Instance(version="")
    result, log_output = compF1_2(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

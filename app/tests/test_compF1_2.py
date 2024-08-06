import pytest
from io import StringIO
import logging

# Assuming compF1_2 is imported from the module where it's defined
from app.services.f_indicators import compF1_2

class MockInstance:
    def __init__(self, version):
        self.version = version

# Ensure that the logger captures the output
@pytest.fixture
def caplog(caplog):
    return caplog

def test_compF1_2_valid_version(caplog):
    instance = MockInstance(version="1.0.0")
    result, log_output = compF1_2(instance)
    assert result == True
    assert "Version is valid." in log_output
    assert "Version provided: 1.0.0" in log_output

def test_compF1_2_invalid_version_parts(caplog):
    instance = MockInstance(version="1")
    result, log_output = compF1_2(instance)
    assert result == False
    assert "Version does not have enough parts (should be at least major.minor)." in log_output

def test_compF1_2_invalid_version_digit(caplog):
    instance = MockInstance(version="1.a")
    result, log_output = compF1_2(instance)
    assert result == False
    assert "Part 'a' is not a digit." in log_output

def test_compF1_2_no_version(caplog):
    instance = MockInstance(version="")
    result, log_output = compF1_2(instance)
    assert result == False
    assert "No version provided." in log_output

if __name__ == "__main__":
    pytest.main()

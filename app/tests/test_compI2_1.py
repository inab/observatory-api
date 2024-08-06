import pytest

from app.services.i_indicators import compI2_1

class MockInstance:
    def __init__(self, type):
        self.type = type

def test_compI2_1_with_lib_type():
    instance = MockInstance(type="lib")
    result, logs = compI2_1(instance)
    assert result == True

def test_compI2_1_with_rest_type():
    instance = MockInstance(type="rest")
    result, logs = compI2_1(instance)
    assert result == True

def test_compI2_1_with_soap_type():
    instance = MockInstance(type="soap")
    result, logs = compI2_1(instance)
    assert result == True

def test_compI2_1_with_api_type():
    instance = MockInstance(type="api")
    result, logs = compI2_1(instance)
    assert result == True

def test_compI2_1_with_other_type():
    instance = MockInstance(type="other")
    result, logs = compI2_1(instance)
    assert result == False

def test_compI2_1_with_none_type():
    instance = MockInstance(type=None)
    result, logs = compI2_1(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

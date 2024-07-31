import pytest

from app.services.i_indicators import compI2_1

class MockInstance:
    def __init__(self, type):
        self.type = type

def test_compI2_1_with_lib_type():
    instance = MockInstance(type="lib")
    assert compI2_1(instance) == True

def test_compI2_1_with_rest_type():
    instance = MockInstance(type="rest")
    assert compI2_1(instance) == True

def test_compI2_1_with_soap_type():
    instance = MockInstance(type="soap")
    assert compI2_1(instance) == True

def test_compI2_1_with_api_type():
    instance = MockInstance(type="api")
    assert compI2_1(instance) == True

def test_compI2_1_with_other_type():
    instance = MockInstance(type="other")
    assert compI2_1(instance) == False

def test_compI2_1_with_none_type():
    instance = MockInstance(type=None)
    assert compI2_1(instance) == False

if __name__ == "__main__":
    pytest.main()

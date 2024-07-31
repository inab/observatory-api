import pytest

# Assuming compF1_2 is imported from the module where it's defined
from app.services.f_indicators import compF1_2

class MockInstance:
    def __init__(self, version):
        self.version = version

def test_compF1_2_with_valid_version():
    '''
    Should return True for a valid version
    '''
    instance = MockInstance(version="1.0")
    assert compF1_2(instance) == True

def test_compF1_2_with_invalid_version():
    instance = MockInstance(version="1")
    assert compF1_2(instance) == False

def test_compF1_2_with_empty_version():
    instance = MockInstance(version="")
    assert compF1_2(instance) == False

def test_compF1_2_with_none_version():
    instance = MockInstance(version=None)
    assert compF1_2(instance) == False

def test_compF1_2_with_complex_valid_version():
    instance = MockInstance(version="2.3.4")
    assert compF1_2(instance) == True

def test_compF1_2_with_invalid_format_version():
    instance = MockInstance(version="a.b")
    assert compF1_2(instance) == False

if __name__ == "__main__":
    pytest.main()

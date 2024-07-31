import pytest

from app.services.a_indicators import compA1_5

class MockInstance:
    def __init__(self, super_type, src):
        self.super_type = super_type
        self.src = src

def test_compA1_5_with_no_web_and_source_code():
    instance = MockInstance(super_type='no_web', src=["https://example.com/src"])
    assert compA1_5(instance) == True

def test_compA1_5_with_no_web_and_no_source_code():
    instance = MockInstance(super_type='no_web', src=[])
    assert compA1_5(instance) == False

def test_compA1_5_with_web_and_source_code():
    instance = MockInstance(super_type='web', src=["https://example.com/src"])
    assert compA1_5(instance) == False

def test_compA1_5_with_web_and_no_source_code():
    instance = MockInstance(super_type='web', src=[])
    assert compA1_5(instance) == False

def test_compA1_5_with_none_super_type():
    instance = MockInstance(super_type=None, src=[])
    assert compA1_5(instance) == False

def test_compA1_5_with_none_src():
    instance = MockInstance(super_type='no_web', src=None)
    assert compA1_5(instance) == False

if __name__ == "__main__":
    pytest.main()

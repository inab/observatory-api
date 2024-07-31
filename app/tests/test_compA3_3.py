import pytest

from app.services.a_indicators import compA3_3

class MockInstance:
    def __init__(self, super_type, os):
        self.super_type = super_type
        self.os = os

def test_compA3_3_with_no_web_and_multiple_os():
    instance = MockInstance(super_type='no_web', os=["Linux", "Windows"])
    assert compA3_3(instance) == True

def test_compA3_3_with_no_web_and_single_os():
    instance = MockInstance(super_type='no_web', os=["Linux"])
    assert compA3_3(instance) == False

def test_compA3_3_with_no_web_and_no_os():
    instance = MockInstance(super_type='no_web', os=[])
    assert compA3_3(instance) == False

def test_compA3_3_with_no_web_and_none_os():
    instance = MockInstance(super_type='no_web', os=None)
    assert compA3_3(instance) == False

def test_compA3_3_with_web_and_multiple_os():
    instance = MockInstance(super_type='web', os=["Linux", "Windows"])
    assert compA3_3(instance) == False

def test_compA3_3_with_web_and_single_os():
    instance = MockInstance(super_type='web', os=["Linux"])
    assert compA3_3(instance) == False

def test_compA3_3_with_web_and_no_os():
    instance = MockInstance(super_type='web', os=[])
    assert compA3_3(instance) == False

def test_compA3_3_with_web_and_none_os():
    instance = MockInstance(super_type='web', os=None)
    assert compA3_3(instance) == False

def test_compA3_3_with_none_super_type():
    instance = MockInstance(super_type=None, os=["Linux", "Windows"])
    assert compA3_3(instance) == False

if __name__ == "__main__":
    pytest.main()

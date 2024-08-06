import pytest

from app.services.a_indicators import compA3_2

class MockInstance:
    def __init__(self, super_type, os):
        self.super_type = super_type
        self.os = os

def test_compA3_2_with_no_web_and_free_os():
    instance = MockInstance(super_type='no_web', os=["Linux"])
    result, logs = compA3_2(instance)
    assert result == True

def test_compA3_2_with_no_web_and_non_free_os():
    instance = MockInstance(super_type='no_web', os=["Windows"])
    result, logs = compA3_2(instance)
    assert result == False

def test_compA3_2_with_no_web_and_mixed_os():
    instance = MockInstance(super_type='no_web', os=["Linux", "Windows"])
    result, logs = compA3_2(instance)
    assert result == True

def test_compA3_2_with_no_web_and_mixed_os_lower():
    instance = MockInstance(super_type='no_web', os=["linux", "Windows"])
    result, logs = compA3_2(instance)
    assert result == True


def test_compA3_2_with_no_web_and_empty_os():
    instance = MockInstance(super_type='no_web', os=[])
    result, logs = compA3_2(instance)
    assert result == False


def test_compA3_2_with_no_web_and_none_os():
    instance = MockInstance(super_type='no_web', os=None)
    result, logs = compA3_2(instance)
    assert result == False


def test_compA3_2_with_web():
    instance = MockInstance(super_type='web', os=["Linux"])
    result, logs = compA3_2(instance)
    assert result == True    

def test_compA3_2_with_none_super_type():
    instance = MockInstance(super_type=None, os=["Linux"])
    result, logs = compA3_2(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()

import pytest

from app.services.a_indicators import compA3_2

class MockInstance:
    def __init__(self, super_type, os):
        self.super_type = super_type
        self.os = os

def test_compA3_2_with_no_web_and_free_os():
    instance = MockInstance(super_type='no_web', os=["Linux"])
    assert compA3_2(instance) == True

def test_compA3_2_with_no_web_and_non_free_os():
    instance = MockInstance(super_type='no_web', os=["Windows"])
    assert compA3_2(instance) == False

def test_compA3_2_with_no_web_and_mixed_os():
    instance = MockInstance(super_type='no_web', os=["Linux", "Windows"])
    assert compA3_2(instance) == True


def test_compA3_2_with_no_web_and_mixed_os_lower():
    instance = MockInstance(super_type='no_web', os=["linux", "Windows"])
    assert compA3_2(instance) == True


def test_compA3_2_with_no_web_and_empty_os():
    instance = MockInstance(super_type='no_web', os=[])
    assert compA3_2(instance) == False

def test_compA3_2_with_no_web_and_none_os():
    instance = MockInstance(super_type='no_web', os=None)
    assert compA3_2(instance) == False

def test_compA3_2_with_web():
    instance = MockInstance(super_type='web', os=["Linux"])
    assert compA3_2(instance) == True

def test_compA3_2_with_none_super_type():
    instance = MockInstance(super_type=None, os=["Linux"])
    assert compA3_2(instance) == True

if __name__ == "__main__":
    pytest.main()

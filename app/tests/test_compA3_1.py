import pytest

from app.services.a_indicators import compA3_1

class MockInstance:
    def __init__(self, registration_not_mandatory):
        self.registration_not_mandatory = registration_not_mandatory

def test_compA3_1_with_registration_not_mandatory_true():
    instance = MockInstance(registration_not_mandatory=True)
    assert compA3_1(instance) == True

def test_compA3_1_with_registration_not_mandatory_false():
    instance = MockInstance(registration_not_mandatory=False)
    assert compA3_1(instance) == False

def test_compA3_1_with_registration_not_mandatory_none():
    instance = MockInstance(registration_not_mandatory=None)
    assert compA3_1(instance) == False

if __name__ == "__main__":
    pytest.main()

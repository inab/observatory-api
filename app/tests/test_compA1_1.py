import pytest

from app.services.a_indicators import compA1_1

class MockInstance:
    def __init__(self, operational):
        self.operational = operational

def test_compA1_1_with_operational_true():
    instance = MockInstance(operational=True)
    assert compA1_1(instance) == True

def test_compA1_1_with_operational_false():
    instance = MockInstance(operational=False)
    assert compA1_1(instance) == False

def test_compA1_1_with_operational_none():
    instance = MockInstance(operational=None)
    assert compA1_1(instance) == False

if __name__ == "__main__":
    pytest.main()

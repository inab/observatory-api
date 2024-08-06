import pytest

from app.services.a_indicators import compA1_1

class MockInstance:
    def __init__(self, operational):
        self.operational = operational

def test_compA1_1_with_operational_true():
    instance = MockInstance(operational=True)
    result, logs = compA1_1(instance)
    assert result == True

def test_compA1_1_with_operational_false():
    instance = MockInstance(operational=False)
    result, logs = compA1_1(instance)
    assert result == False

def test_compA1_1_with_operational_none():
    instance = MockInstance(operational=None)
    result, logs = compA1_1(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

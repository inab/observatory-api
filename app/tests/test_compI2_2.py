import pytest

from app.services.i_indicators import compI2_2

class MockInstance:
    def __init__(self, source):
        self.source = source

def test_compI2_2_with_galaxy_source():
    instance = MockInstance(source=['galaxy'])
    result, logs = compI2_2(instance)
    assert result == True

def test_compI2_2_with_toolshed_source():
    instance = MockInstance(source=['toolshed'])
    result, logs = compI2_2(instance)
    assert result == True

def test_compI2_2_with_galaxy_and_toolshed_sources():
    instance = MockInstance(source=['galaxy', 'toolshed'])
    result, logs = compI2_2(instance)
    assert result == True

def test_compI2_2_with_other_source():
    instance = MockInstance(source=['other'])
    result, logs = compI2_2(instance)
    assert result == False

def test_compI2_2_with_mixed_sources():
    instance = MockInstance(source=['galaxy', 'other'])
    result, logs = compI2_2(instance)
    assert result == True

def test_compI2_2_with_empty_source():
    instance = MockInstance(source=[])
    result, logs = compI2_2(instance)
    assert result == False

def test_compI2_2_with_none_source():
    instance = MockInstance(source=None)
    result, logs = compI2_2(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

import pytest

from app.services.i_indicators import compI2_2

class MockInstance:
    def __init__(self, source):
        self.source = source

def test_compI2_2_with_galaxy_source():
    instance = MockInstance(source=['galaxy'])
    assert compI2_2(instance) == True

def test_compI2_2_with_toolshed_source():
    instance = MockInstance(source=['toolshed'])
    assert compI2_2(instance) == True

def test_compI2_2_with_galaxy_and_toolshed_sources():
    instance = MockInstance(source=['galaxy', 'toolshed'])
    assert compI2_2(instance) == True

def test_compI2_2_with_other_source():
    instance = MockInstance(source=['other'])
    assert compI2_2(instance) == False

def test_compI2_2_with_mixed_sources():
    instance = MockInstance(source=['galaxy', 'other'])
    assert compI2_2(instance) == True

def test_compI2_2_with_empty_source():
    instance = MockInstance(source=[])
    assert compI2_2(instance) == False

def test_compI2_2_with_none_source():
    instance = MockInstance(source=None)
    assert compI2_2(instance) == False

if __name__ == "__main__":
    pytest.main()

import pytest

from app.services.f_indicators import compF2_1

class MockInstance:
    def __init__(self, source):
        self.source = source

def test_compF2_1_with_structured_sources():
    instance = MockInstance(source=["biotools", "github"])
    assert compF2_1(instance) == True

def test_compF2_1_with_unstructured_sources():
    instance = MockInstance(source=["random_source", "another_source"])
    assert compF2_1(instance) == False

def test_compF2_1_with_mixed_sources():
    instance = MockInstance(source=["biotools", "random_source"])
    assert compF2_1(instance) == True

def test_compF2_1_with_empty_sources():
    instance = MockInstance(source=[])
    assert compF2_1(instance) == False

def test_compF2_1_with_none_sources():
    instance = MockInstance(source=None)
    assert compF2_1(instance) == False

def test_compF2_1_with_only_one_structured_source():
    instance = MockInstance(source=["galaxy"])
    assert compF2_1(instance) == True

if __name__ == "__main__":
    pytest.main()

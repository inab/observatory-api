import pytest

from app.services.f_indicators import compF2_1

class MockInstance:
    def __init__(self, source):
        self.source = source

def test_compF2_1_with_structured_sources():
    instance = MockInstance(source=["biotools", "github"])
    result, logs = compF2_1(instance)
    assert result == True
    assert "Received source: ['biotools', 'github']" in logs
    assert "Source 'biotools' matches structured metadata. Returning True." in logs

def test_compF2_1_with_unstructured_sources():
    instance = MockInstance(source=["random_source", "another_source"])
    result, logs = compF2_1(instance)
    assert result == False
    assert "Received source: ['random_source', 'another_source']" in logs
    assert "No sources match structured metadata. Returning False." in logs

def test_compF2_1_with_mixed_sources():
    instance = MockInstance(source=["biotools", "random_source"])
    result, logs = compF2_1(instance)
    assert result == True
    assert "Received source: ['biotools', 'random_source']" in logs
    assert "Source 'biotools' matches structured metadata. Returning True." in logs

def test_compF2_1_with_empty_sources():
    instance = MockInstance(source=[])
    result, logs = compF2_1(instance)
    assert result == False
    assert "Received source: []" in logs
    assert "Source is empty. Returning False." in logs

def test_compF2_1_with_none_sources():
    instance = MockInstance(source=None)
    result, logs = compF2_1(instance)
    assert result == False
    assert "Received source: None" in logs
    assert "Source is None. Returning False." in logs

def test_compF2_1_with_only_one_structured_source():
    instance = MockInstance(source=["galaxy"])
    result, logs = compF2_1(instance)
    assert result == True
    assert "Received source: ['galaxy']" in logs
    assert "Source 'galaxy' matches structured metadata. Returning True." in logs

if __name__ == "__main__":
    pytest.main()
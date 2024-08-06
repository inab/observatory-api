import pytest

# Assuming compF3_1 is imported from the module where it's defined
from app.services.f_indicators import compF3_1

class MockInstance:
    def __init__(self, source):
        self.source = source

def test_compF3_1_with_valid_sources():
    instance = MockInstance(source=["github", "npm"])
    result, logs = compF3_1(instance)
    assert result == True

def test_compF3_1_with_invalid_sources():
    instance = MockInstance(source=["random_source", "another_source"])
    result, logs = compF3_1(instance)
    assert result == False

def test_compF3_1_with_mixed_sources():
    instance = MockInstance(source=["github", "random_source"])
    result, logs = compF3_1(instance)
    assert result == True

def test_compF3_1_with_empty_sources():
    instance = MockInstance(source=[])
    result, logs = compF3_1(instance)
    assert result == False


def test_compF3_1_with_none_sources():
    instance = MockInstance(source=None)
    result, logs = compF3_1(instance)
    assert result == False

def test_compF3_1_with_case_insensitive_sources():
    instance = MockInstance(source=["GiThUb", "NPM"])
    result, logs = compF3_1(instance)
    assert result == True

def test_compF3_1_with_only_one_valid_source():
    instance = MockInstance(source=["bitbucket"])
    result, logs = compF3_1(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()

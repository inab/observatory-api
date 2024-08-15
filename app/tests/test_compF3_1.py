import pytest

from app.services.f_indicators import compF3_1
from app.models.instance import Instance


def test_compF3_1_with_valid_registry():
    instance = Instance(registries=["npm"])
    result, logs = compF3_1(instance)
    assert result == True

def test_compF3_1_with_valid_source():
    instance = Instance(source=["bioconductor"])
    result, logs = compF3_1(instance)
    assert result == True

def test_compF3_1_with_invalid_sources():
    instance = Instance(source=["random_source", "another_source"])
    result, logs = compF3_1(instance)
    assert result == False

def test_compF3_1_with_mixed_sources():
    instance = Instance(source=["github", "random_source"])
    result, logs = compF3_1(instance)
    assert result == False

def test_compF3_1_with_empty_sources():
    instance = Instance(source=[])
    result, logs = compF3_1(instance)
    assert result == False


def test_compF3_1_with_none_sources():
    instance = Instance(source=None)
    result, logs = compF3_1(instance)
    assert result == False

def test_compF3_1_with_case_insensitive_sources():
    instance = Instance(source=["GiThUb"], registries=["npm"])
    result, logs = compF3_1(instance)
    assert result == True

def test_compF3_1_with_only_one_valid_source():
    instance = Instance(source=["bitbucket"])
    result, logs = compF3_1(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

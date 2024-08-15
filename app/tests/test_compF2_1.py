import pytest

from app.services.f_indicators import compF2_1
from app.models.instance import Instance

def test_compF2_1_with_structured_sources():
    instance = Instance(source=["biotools", "github"])
    result, logs = compF2_1(instance)
    assert result == True


def test_compF2_1_with_unstructured_sources():
    instance = Instance(source=["random_source", "another_source"])
    result, logs = compF2_1(instance)
    assert result == False


def test_compF2_1_with_mixed_sources():
    instance = Instance(source=["biotools", "random_source"])
    result, logs = compF2_1(instance)
    assert result == True

def test_compF2_1_with_empty_sources():
    instance = Instance(source=[])
    result, logs = compF2_1(instance)
    assert result == False


def test_compF2_1_with_none_sources():
    instance = Instance(source=None)
    result, logs = compF2_1(instance)
    assert result == False


def test_compF2_1_with_only_one_structured_source():
    instance = Instance(source=["galaxy"])
    result, logs = compF2_1(instance)
    assert result == True


if __name__ == "__main__":
    pytest.main()
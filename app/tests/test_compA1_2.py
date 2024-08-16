import pytest

from app.services.a_indicators import compA1_2
from app.models.instance import Instance

def test_compA1_2_with_no_web_and_download():
    instance = Instance(type='cmd', download=["https://github.com/inab/oeb-visualizations"], source=[])
    result, logs = compA1_2(instance)
    assert result == True

def test_compA1_2_with_cmd_and_valid_source():
    instance = Instance(type='cmd', download=[], source=["bioconda"])
    result, logs = compA1_2(instance)
    assert result == False

def test_compA1_2_with_cmd_and_invalid_source():
    instance = Instance(type='cmd', download=[], source=["random_source"])
    result, logs = compA1_2(instance)
    assert result == False

def test_compA1_2_with_cmd_and_empty_download_and_source():
    instance = Instance(type='cmd', download=[], source=[])
    result, logs = compA1_2(instance)
    assert result == False

def test_compA1_2_with_web_and_valid_download():
    instance = Instance(type='web', download=["https://github.com/inab/oeb-visualizations"], source=[])
    result, logs = compA1_2(instance)
    assert result == False

def test_compA1_2_with_web_and_valid_source():
    instance = Instance(type='web', download=[], source=["bioconda"])
    result, logs = compA1_2(instance)
    assert result == False

def test_compA1_2_with_none_type():
    instance = Instance(type=None, download=[], source=[])
    result, logs = compA1_2(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

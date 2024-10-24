import pytest

from app.services.a_indicators import compA1_5
from app.models.instance import Instance

def test_compA1_5_with_no_web_and_source_code():
    instance = Instance(type='cmd', src=["https://github.com"])
    result, logs = compA1_5(instance)
    assert result == True

def test_compA1_5_with_no_web_and_no_source_code():
    instance = Instance(type='cmd', src=[])
    result, logs = compA1_5(instance)
    assert result == False

def test_compA1_5_with_web_and_source_code():
    instance = Instance(type='web', src=["https://github.com"])
    result, logs = compA1_5(instance)
    assert result == False

def test_compA1_5_with_web_and_no_source_code():
    instance = Instance(type='web', src=[])
    result, logs = compA1_5(instance)
    assert result == False

def test_compA1_5_with_none_type():
    instance = Instance(type=None, src=[])
    result, logs = compA1_5(instance)
    assert result == False

def test_compA1_5_with_none_src():
    instance = Instance(type='lib', src=None)
    result, logs = compA1_5(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

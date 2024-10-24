import pytest
from pydantic import HttpUrl
from app.services.a_indicators import compA1_4
from app.models.instance import Instance, Documentation

#
def test_compA1_4_with_test_data():
    instance = Instance(test=['https://github.com'], documentation=[])
    result, logs = compA1_4(instance)
    assert result == True

def test_compA1_4_with_no_test_data():
    instance = Instance(test=[], documentation=[])
    result, logs = compA1_4(instance)
    assert result == False

def test_compA1_4_with_test_data_in_docs():
    instance = Instance(test=[], documentation=[{'type': 'test data', 'url': 'https://github.com'}])
    result, logs = compA1_4(instance)
    print(logs)
    assert result == True

def test_compA1_4_with_no_test_data_in_docs():
    instance = Instance(test=[], documentation=[{'type': 'other', 'url': 'https://github.com'}])
    result, logs = compA1_4(instance)
    assert result == False

def test_compA1_4_with_mixed_test_data():
    instance = Instance(test=['https://github.com'], documentation=[{'type': 'test data', 'url': 'https://github.com'}])
    result, logs = compA1_4(instance)
    assert result == True

def test_compA1_4_with_none_test():
    instance = Instance(test=[], documentation=[])
    result, logs = compA1_4(instance)
    assert result == False

def test_compA1_4_with_none_documentation():
    instance = Instance(test=[], documentation=None)
    result, logs = compA1_4(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()
import pytest
from pydantic import HttpUrl
from app.services.a_indicators import compA1_4
from app.models.instance import Instance, Documentation

# Define test instances using Pydantic models
def create_instance(test, documentation):
    return Instance(
        test=test,
        documentation=[Documentation(type=doc['type'], url=HttpUrl(doc['url'])) for doc in documentation] if documentation else []
    )

def test_compA1_4_with_test_data():
    instance = create_instance(test=True, documentation=[])
    result, logs = compA1_4(instance)
    assert result == True

def test_compA1_4_with_no_test_data():
    instance = create_instance(test=False, documentation=[])
    result, logs = compA1_4(instance)
    assert result == False

def test_compA1_4_with_test_data_in_docs():
    instance = create_instance(test=False, documentation=[{'type': 'test data', 'url': 'http://example.com/testdata'}])
    result, logs = compA1_4(instance)
    assert result == True

def test_compA1_4_with_no_test_data_in_docs():
    instance = create_instance(test=False, documentation=[{'type': 'other', 'url': 'http://example.com/other'}])
    result, logs = compA1_4(instance)
    assert result == False

def test_compA1_4_with_mixed_test_data():
    instance = create_instance(test=True, documentation=[{'type': 'test data', 'url': 'http://example.com/testdata'}])
    result, logs = compA1_4(instance)
    assert result == True

def test_compA1_4_with_none_test():
    instance = create_instance(test=None, documentation=[])
    result, logs = compA1_4(instance)
    assert result == False

def test_compA1_4_with_none_documentation():
    instance = create_instance(test=False, documentation=None)
    result, logs = compA1_4(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()
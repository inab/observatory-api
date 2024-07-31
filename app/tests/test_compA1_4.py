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
    assert compA1_4(instance) == True

def test_compA1_4_with_no_test_data():
    instance = create_instance(test=False, documentation=[])
    assert compA1_4(instance) == False

def test_compA1_4_with_test_data_in_docs():
    instance = create_instance(test=False, documentation=[{'type': 'test data', 'url': 'http://example.com/testdata'}])
    assert compA1_4(instance) == True

def test_compA1_4_with_no_test_data_in_docs():
    instance = create_instance(test=False, documentation=[{'type': 'other', 'url': 'http://example.com/other'}])
    assert compA1_4(instance) == False

def test_compA1_4_with_mixed_test_data():
    instance = create_instance(test=True, documentation=[{'type': 'test data', 'url': 'http://example.com/testdata'}])
    assert compA1_4(instance) == True

def test_compA1_4_with_none_test():
    instance = create_instance(test=None, documentation=[])
    assert compA1_4(instance) == False

def test_compA1_4_with_none_documentation():
    instance = create_instance(test=False, documentation=None)
    assert compA1_4(instance) == False

if __name__ == "__main__":
    pytest.main()
import pytest
from pydantic import HttpUrl

from app.services.a_indicators import compA1_3
from app.models.instance import Instance, Documentation

# Define test instances using Pydantic models
def create_instance(type, download, source, documentation):
    return Instance(
        type=type,
        download=[HttpUrl(url) for url in download] if download else [],
        source=source,
        documentation=[Documentation(type=doc['type'], url=HttpUrl(doc['url'])) for doc in documentation] if documentation else []
    )

def test_compA1_3_with_no_web_and_download():
    instance = create_instance(
        type='cmd', 
        download=["https://github.com/inab/oeb-visualizations"], 
        source=[], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    assert result == False

def test_compA1_3_with_no_web_and_valid_source():
    instance = create_instance(
        type='lib', 
        download=[], 
        source=["bioconda"], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    assert result == True

def test_compA1_3_with_no_web_and_installation_instructions():
    instance = create_instance(
        type='cmd', 
        download=[], 
        source=[], 
        documentation=[{'type': 'installation instructions', 'url': 'https://github.com/inab/oeb-visualizations'}]
    )
    result, logs = compA1_3(instance)
    print(logs)
    assert result == True

def test_compA1_3_with_no_web_and_invalid_source():
    instance = create_instance(
        type='cmd', 
        download=[], 
        source=["random_source"], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    print(logs)
    assert result == False

def test_compA1_3_with_no_web_and_empty_download_source_and_documentation():
    instance = create_instance(
        type='cmd', 
        download=[], 
        source=[], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    assert result == False

def test_compA1_3_with_web_and_valid_download():
    instance = create_instance(
        type='web', 
        download=["http://github.com/inab/oeb-visualizations"], 
        source=[], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    assert result == False

def test_compA1_3_with_web_and_valid_source():
    instance = create_instance(
        type='web', 
        download=[], 
        source=["bioconda"], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    assert result == False

def test_compA1_3_with_web_and_installation_instructions():
    instance = create_instance(
        type='web', 
        download=[], 
        source=[], 
        documentation=[{'type': 'installation', 'url': 'http://github.com/inab/oeb-visualizations'}]
    )
    result, logs = compA1_3(instance)
    assert result == False

def test_compA1_3_with_none_type():
    instance = create_instance(
        type=None, 
        download=[], 
        source=[], 
        documentation=[]
    )
    result, logs = compA1_3(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

import pytest
from pydantic import HttpUrl

from app.services.a_indicators import compA1_3
from app.models.instance import Instance, Documentation

# Define test instances using Pydantic models
def create_instance(super_type, download, source, documentation):
    return Instance(
        super_type=super_type,
        download=[HttpUrl(url) for url in download] if download else [],
        source=source,
        documentation=[Documentation(type=doc['type'], url=HttpUrl(doc['url'])) for doc in documentation] if documentation else []
    )

def test_compA1_3_with_no_web_and_download():
    instance = create_instance(
        super_type='no_web', 
        download=["http://example.com/download"], 
        source=[], 
        documentation=[]
    )
    assert compA1_3(instance) == True

def test_compA1_3_with_no_web_and_valid_source():
    instance = create_instance(
        super_type='no_web', 
        download=[], 
        source=["bioconda"], 
        documentation=[]
    )
    assert compA1_3(instance) == True

def test_compA1_3_with_no_web_and_installation_instructions():
    instance = create_instance(
        super_type='no_web', 
        download=[], 
        source=[], 
        documentation=[{'type': 'installation', 'url': 'http://example.com/install'}]
    )
    assert compA1_3(instance) == True

def test_compA1_3_with_no_web_and_invalid_source():
    instance = create_instance(
        super_type='no_web', 
        download=[], 
        source=["random_source"], 
        documentation=[]
    )
    assert compA1_3(instance) == False

def test_compA1_3_with_no_web_and_empty_download_source_and_documentation():
    instance = create_instance(
        super_type='no_web', 
        download=[], 
        source=[], 
        documentation=[]
    )
    assert compA1_3(instance) == False

def test_compA1_3_with_web_and_valid_download():
    instance = create_instance(
        super_type='web', 
        download=["http://example.com/download"], 
        source=[], 
        documentation=[]
    )
    assert compA1_3(instance) == False

def test_compA1_3_with_web_and_valid_source():
    instance = create_instance(
        super_type='web', 
        download=[], 
        source=["bioconda"], 
        documentation=[]
    )
    assert compA1_3(instance) == False

def test_compA1_3_with_web_and_installation_instructions():
    instance = create_instance(
        super_type='web', 
        download=[], 
        source=[], 
        documentation=[{'type': 'installation', 'url': 'http://example.com/install'}]
    )
    assert compA1_3(instance) == False

def test_compA1_3_with_none_super_type():
    instance = create_instance(
        super_type=None, 
        download=[], 
        source=[], 
        documentation=[]
    )
    assert compA1_3(instance) == False

if __name__ == "__main__":
    pytest.main()

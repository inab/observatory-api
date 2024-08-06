from app.models.instance import Documentation, Instance
from app.services.r_indicators import compR4_2

# Test cases for compR4_2 function
def test_compR4_2_with_release_policy():
    # Case where a document type matches 'release policy'
    docs = [Documentation(type='release policy')]
    instance = Instance(documentation=docs)
    result, logs = compR4_2(instance)
    assert result == True

def test_compR4_2_with_version_release_policy():
    # Case where a document type matches 'version release policy'
    docs = [Documentation(type='version release policy')]
    instance = Instance(documentation=docs)
    result, logs = compR4_2(instance)
    assert result == True

def test_compR4_2_with_distribution_policy():
    # Case where a document type matches 'distribution policy'
    docs = [Documentation(type='distribution policy')]
    instance = Instance(documentation=docs)
    result, logs = compR4_2(instance)
    assert result == True

def test_compR4_2_with_no_matching_synonyms():
    # Case where no document type matches any of the synonyms
    docs = [Documentation(type='usage guide')]
    instance = Instance(documentation=docs)
    result, logs = compR4_2(instance)
    assert result == False

def test_compR4_2_with_mixed_document_types():
    # Case where some document types match and others do not
    docs = [
        Documentation(type='usage guide'),
        Documentation(type='deployment policy')
    ]
    instance = Instance(documentation=docs)
    result, logs = compR4_2(instance)
    assert result == True

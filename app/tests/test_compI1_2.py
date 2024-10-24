import pytest
from app.models.instance import Instance, Documentation
from app.services.i_indicators import compI1_2

def test_compI1_2_with_api_specification():
    docs=[Documentation(type="API specification", url="https://github.com")]
    instance = Instance(documentation=docs, type='rest')
    result, logs = compI1_2(instance)
    assert result == True

def test_compI1_2_with_multiple_documentations_including_api_specification():
    docs=[
        Documentation(type="General documentation", url="https://github.com"),
        Documentation(type="API specification", url="https://github.com")
    ]
    instance = Instance(documentation=docs, type='rest')
    result, logs = compI1_2(instance)
    assert result == True

def test_compI1_2_with_no_api_specification():
    docs=[Documentation(type="General documentation", url="https://github.com")]
    instance = Instance(documentation=docs)
    result, logs = compI1_2(instance)
    assert result == False

def test_compI1_2_with_empty_documentation():
    instance = Instance(documentation=[])
    result, logs = compI1_2(instance)
    assert result == False

def test_compI1_2_with_none_documentation():
    instance = Instance(documentation=None)
    result, logs = compI1_2(instance)
    assert result == False

def test_compI1_2_with_invalid_documentation_format():
    docs=[Documentation(type="API specification", ul="https://inab.github.io/oeb-visualizations/")]
    instance = Instance(documentation=docs)
    result, logs = compI1_2(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

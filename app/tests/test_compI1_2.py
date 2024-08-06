import pytest
from app.models.instance import Instance, Documentation
from app.services.i_indicators import compI1_2

# Define a helper function to create an Instance with documentation
def create_instance(documentation):
    return Instance(
        documentation=documentation
    )

def test_compI1_2_with_api_specification():
    instance = create_instance([Documentation(type="API specification")])
    result, logs = compI1_2(instance)
    assert result == True

def test_compI1_2_with_multiple_documentations_including_api_specification():
    instance = create_instance([
        Documentation(type="General documentation"),
        Documentation(type="API specification")
    ])
    result, logs = compI1_2(instance)
    assert result == True

def test_compI1_2_with_no_api_specification():
    instance = create_instance([Documentation(type="General documentation")])
    result, logs = compI1_2(instance)
    assert result == False

def test_compI1_2_with_empty_documentation():
    instance = create_instance([])
    result, logs = compI1_2(instance)
    assert result == False

def test_compI1_2_with_none_documentation():
    instance = create_instance(None)
    result, logs = compI1_2(instance)
    assert result == False

def test_compI1_2_with_invalid_documentation_format():
    instance = create_instance([Documentation(type="wrong_type", url="http://example.com")])
    result, logs = compI1_2(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

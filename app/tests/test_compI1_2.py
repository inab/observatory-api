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
    assert compI1_2(instance) == True

def test_compI1_2_with_multiple_documentations_including_api_specification():
    instance = create_instance([
        Documentation(type="General documentation"),
        Documentation(type="API specification")
    ])
    assert compI1_2(instance) == True

def test_compI1_2_with_no_api_specification():
    instance = create_instance([Documentation(type="General documentation")])
    assert compI1_2(instance) == False

def test_compI1_2_with_empty_documentation():
    instance = create_instance([])
    assert compI1_2(instance) == False

def test_compI1_2_with_none_documentation():
    instance = create_instance(None)
    assert compI1_2(instance) == False

def test_compI1_2_with_invalid_documentation_format():
    instance = create_instance([Documentation(type="wrong_type", url="http://example.com")])
    assert compI1_2(instance) == False

if __name__ == "__main__":
    pytest.main()

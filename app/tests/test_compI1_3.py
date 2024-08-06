import pytest
from app.models.instance import Instance
from app.services.i_indicators import compI1_3

# Define a helper function to create an Instance with input and output
def create_instance(input_data, output_data):
    return Instance(
        input=input_data,
        output=output_data
    )

def test_compI1_3_with_verifiable_input_format():
    instance = create_instance([{"term": "json"}], [])
    result, logs = compI1_3(instance)
    assert result == True

def test_compI1_3_with_verifiable_output_format():
    instance = create_instance([], [{"term": "xml"}])
    result, logs = compI1_3(instance)
    assert result == True

def test_compI1_3_with_verifiable_input_and_output_format():
    instance = create_instance([{"term": "rdf"}], [{"term": "xds"}])
    result, logs = compI1_3(instance)
    assert result == True

def test_compI1_3_with_non_verifiable_formats():
    instance = create_instance([{"term": "txt"}], [{"term": "doc"}])
    result, logs = compI1_3(instance)
    assert result == False

def test_compI1_3_with_empty_input_and_output():
    instance = create_instance([], [])
    result, logs = compI1_3(instance)
    assert result == False

def test_compI1_3_with_none_input_and_output():
    instance = create_instance(None, None)
    result, logs = compI1_3(instance)
    assert result == False

def test_compI1_3_with_none_input_and_verifiable_output_format():
    instance = create_instance(None, [{"term": "yaml"}])
    result, logs = compI1_3(instance)
    assert result == True

def test_compI1_3_with_verifiable_input_format_and_none_output():
    instance = create_instance([{"term": "avro"}], None)
    result, logs = compI1_3(instance)
    assert result == True

def test_compI1_3_with_vocabulary_in_input():
    instance = create_instance([{"vocabulary": "EDAM", "term": "FASTA"}], [])
    result, logs = compI1_3(instance)
    assert result == False

def test_compI1_3_with_vocabulary_in_output():
    instance = create_instance([], [{"vocabulary": "EDAM", "term": "FASTA"}])
    result, logs = compI1_3(instance)
    assert result == False

def test_compI1_3_with_vocabulary_in_input_and_output():
    instance = create_instance(
        [{"vocabulary": "EDAM", "term": "JSON"}],
        [{"vocabulary": "EDAM", "term": "CSV"}]
    )
    result, logs = compI1_3(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()
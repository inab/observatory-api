import pytest
from app.services.i_indicators import compI1_1
from app.models.instance import Instance

def create_instance(input, output):
    return Instance(
        input=input,
        output=output
    )

def test_compI1_1_with_valid_input_vocabulary():
    instance = create_instance(input=[{"vocabulary": "EDAM"}], output=[])
    result, logs = compI1_1(instance)
    assert result == True

def test_compI1_1_with_valid_output_vocabulary():
    instance = create_instance(input=[], output=[{"vocabulary": "EDAM"}])
    result, logs = compI1_1(instance)
    assert result == True

def test_compI1_1_with_valid_input_and_output_vocabulary():
    instance = create_instance(input=[{"vocabulary": "EDAM"}], output=[{"vocabulary": "EDAM"}])
    result, logs = compI1_1(instance)
    assert result == True

def test_compI1_1_with_no_vocabulary():
    instance = create_instance(input=[{"vocabulary": ""}], output=[{"vocabulary": ""}])
    result, logs = compI1_1(instance)
    assert result == False

def test_compI1_1_with_empty_input_and_output():
    instance = create_instance(input=[], output=[])
    result, logs = compI1_1(instance)
    assert result == False

def test_compI1_1_with_none_input_and_output():
    instance = create_instance(input=None, output=None)
    result, logs = compI1_1(instance)
    assert result == False

def test_compI1_1_with_none_input_and_valid_output_vocabulary():
    instance = create_instance(input=None, output=[{"vocabulary": "EDAM"}])
    result, logs = compI1_1(instance)
    assert result == True

def test_compI1_1_with_valid_input_vocabulary_and_none_output():
    instance = create_instance(input=[{"vocabulary": "EDAM"}], output=None)
    result, logs = compI1_1(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()

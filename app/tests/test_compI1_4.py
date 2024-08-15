import pytest
from app.models.instance import Documentation, Instance


from app.services.i_indicators import compI1_4


def test_compI1_4_with_multiple_input_and_output_formats():
    instance = Instance(input=[{"format": "json"}, {"format": "xml"}], output=[{"format": "rdf"}, {"format": "xds"}])
    result, logs = compI1_4(instance)
    assert result == True

def test_compI1_4_with_single_input_and_multiple_output_formats():
    instance = Instance(input=[{"format": "json"}], output=[{"format": "rdf"}, {"format": "xds"}])
    result, logs = compI1_4(instance)
    assert result == False

def test_compI1_4_with_multiple_input_and_single_output_format():
    instance = Instance(input=[{"format": "json"}, {"format": "xml"}], output=[{"format": "rdf"}])
    result, logs = compI1_4(instance)
    assert result == False

def test_compI1_4_with_single_input_and_single_output_format():
    instance = Instance(input=[{"format": "json"}], output=[{"format": "rdf"}])
    result, logs = compI1_4(instance)
    assert result == False

def test_compI1_4_with_empty_input_and_output():
    instance = Instance(input=[], output=[])
    result, logs = compI1_4(instance)
    assert result == False

def test_compI1_4_with_none_input_and_output():
    instance = Instance(input=None, output=None)
    result, logs = compI1_4(instance)
    assert result == False

def test_compI1_4_with_none_input_and_multiple_output_formats():
    instance = Instance(input=None, output=[{"format": "rdf"}, {"format": "xds"}])
    result, logs = compI1_4(instance)
    assert result == False

def test_compI1_4_with_multiple_input_formats_and_none_output():
    instance = Instance(input=[{"format": "json"}, {"format": "xml"}], output=None)
    result, logs = compI1_4(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

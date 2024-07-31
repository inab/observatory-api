import pytest

from app.services.i_indicators import compI1_4

class MockInstance:
    def __init__(self, input, output):
        self.input = input
        self.output = output

def test_compI1_4_with_multiple_input_and_output_formats():
    instance = MockInstance(input=[{"format": "json"}, {"format": "xml"}], output=[{"format": "rdf"}, {"format": "xds"}])
    assert compI1_4(instance) == True

def test_compI1_4_with_single_input_and_multiple_output_formats():
    instance = MockInstance(input=[{"format": "json"}], output=[{"format": "rdf"}, {"format": "xds"}])
    assert compI1_4(instance) == False

def test_compI1_4_with_multiple_input_and_single_output_format():
    instance = MockInstance(input=[{"format": "json"}, {"format": "xml"}], output=[{"format": "rdf"}])
    assert compI1_4(instance) == False

def test_compI1_4_with_single_input_and_single_output_format():
    instance = MockInstance(input=[{"format": "json"}], output=[{"format": "rdf"}])
    assert compI1_4(instance) == False

def test_compI1_4_with_empty_input_and_output():
    instance = MockInstance(input=[], output=[])
    assert compI1_4(instance) == False

def test_compI1_4_with_none_input_and_output():
    instance = MockInstance(input=None, output=None)
    assert compI1_4(instance) == False

def test_compI1_4_with_none_input_and_multiple_output_formats():
    instance = MockInstance(input=None, output=[{"format": "rdf"}, {"format": "xds"}])
    assert compI1_4(instance) == False

def test_compI1_4_with_multiple_input_formats_and_none_output():
    instance = MockInstance(input=[{"format": "json"}, {"format": "xml"}], output=None)
    assert compI1_4(instance) == False

if __name__ == "__main__":
    pytest.main()

import pytest

from app.services.f_indicators import compF2_2
from app.models.instance import Instance
from app.models.instance import ControlledTerm

def test_compF2_2_with_valid_vocabulary():
    topics = [ControlledTerm(vocabulary="EDAM", term="genomics")]
    operations = [ControlledTerm(vocabulary="EDAM", term="variant calling")
    ]
    instance = Instance(topics=topics, operations=operations)
    result, logs = compF2_2(instance)
    assert result == True

def test_compF2_2_with_invalid_vocabulary():
    topics = [ControlledTerm(vocabulary="", term="random_topic")]
    operations = [ControlledTerm(vocabulary="", term="random_operation")]
    instance = Instance(topics=topics, operations=operations)   
    result, logs = compF2_2(instance)
    assert result == False

def test_compF2_2_with_mixed_vocabulary():
    topics = [ControlledTerm(vocabulary="EDAM", term="genomics"), ControlledTerm(vocabulary="", term="random_topic")]
    operations = [ControlledTerm(vocabulary="EDAM", term="variant calling"), ControlledTerm(vocabulary="", term="random_operation")]    
    instance = Instance(topics=topics, operations=operations)
    result, logs = compF2_2(instance)
    assert result == True

def test_compF2_2_with_empty_topics_and_operations():
    instance = Instance(topics=[], operations=[])
    result,logs = compF2_2(instance)
    assert result == False


def test_compF2_2_with_none_topics_and_operations():
    instance = Instance(topics=None, operations=None)
    result, logs = compF2_2(instance)
    assert result ==  False

def test_compF2_2_with_only_valid_topics():
    topics = [ControlledTerm(vocabulary="EDAM", term="metabolomics")]
    operations = []
    instance = Instance(topics=topics, operations=operations)
    result,logs = compF2_2(instance)
    assert result == True

def test_compF2_2_with_only_valid_operations():
    topics = []
    operations = [ControlledTerm(vocabulary="CustomVocab", term="custom_operation")]
    instance = Instance(topics=topics, operations=operations)
    result,logs = compF2_2(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()
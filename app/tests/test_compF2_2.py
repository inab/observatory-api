import pytest

from app.services.f_indicators import compF2_2


class MockTerm:
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

class MockInstance:
    def __init__(self, topics, operations):
        self.topics = topics or []
        self.operations = operations or []

def test_compF2_2_with_valid_vocabulary():
    topics = [MockTerm(vocabulary="EDAM")]
    operations = [MockTerm(vocabulary="CustomVocab")]
    instance = MockInstance(topics=topics, operations=operations)
    result, logs = compF2_2(instance)
    assert result == True

def test_compF2_2_with_invalid_vocabulary():
    topics = [MockTerm(vocabulary="")]
    operations = [MockTerm(vocabulary="")]
    instance = MockInstance(topics=topics, operations=operations)
    result, logs = compF2_2(instance)
    assert result == False

def test_compF2_2_with_mixed_vocabulary():
    topics = [MockTerm(vocabulary="EDAM")]
    operations = [MockTerm(vocabulary="")]
    instance = MockInstance(topics=topics, operations=operations)
    result, logs = compF2_2(instance)
    assert result == True

def test_compF2_2_with_empty_topics_and_operations():
    instance = MockInstance(topics=[], operations=[])
    result,logs = compF2_2(instance)
    assert result == False


def test_compF2_2_with_none_topics_and_operations():
    instance = MockInstance(topics=None, operations=None)
    result, logs = compF2_2(instance)
    assert result ==  False

def test_compF2_2_with_only_valid_topics():
    topics = [MockTerm(vocabulary="EDAM")]
    operations = []
    instance = MockInstance(topics=topics, operations=operations)
    result,logs = compF2_2(instance)
    assert result == True

def test_compF2_2_with_only_valid_operations():
    topics = []
    operations = [MockTerm(vocabulary="CustomVocab")]
    instance = MockInstance(topics=topics, operations=operations)
    result,logs = compF2_2(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()
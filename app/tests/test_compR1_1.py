import pytest
from app.models.instance import Documentation, Instance

from app.services.r_indicators import compR1_1

# Test cases
def test_compR1_1_with_usage_guide():
    instance = Instance(documentation=[Documentation(type='usage guide', url='https://github.com')])
    result, logs = compR1_1(instance)
    assert result == True

def test_compR1_1_with_usage_guide_no_op_url():
    instance = Instance(documentation=[Documentation(type='usage guide', url='https://githubbbb.com')])
    result, logs = compR1_1(instance)
    assert result == False


def test_compR1_1_with_license():
    instance = Instance(documentation=[Documentation(type='license')])
    result, logs = compR1_1(instance)
    assert result == False

def test_compR1_1_with_mixed_docs():
    instance = Instance(documentation=[
        Documentation(type='license', url='https://github.com'), 
        Documentation(type='usage guide', url='https://github.com')
    ])
    result, logs = compR1_1(instance)
    assert result == True

def test_compR1_1_with_no_guide_docs():
    instance = Instance(documentation=[
        Documentation(type='license'), 
        Documentation(type='terms of use')
    ])
    result, logs = compR1_1(instance)
    assert result == False

def test_compR1_1_with_empty_docs():
    instance = Instance(documentation=[])
    result, logs = compR1_1(instance)
    assert result == False

def test_compR1_1_with_none_docs():
    instance = Instance(documentation=None)
    result, logs = compR1_1(instance)
    assert result == False

def test_compR1_1_with_case_insensitive_check():
    instance = Instance(documentation=[Documentation(type='UsAgE GuIdE', url='https://github.com')])
    result, logs = compR1_1(instance)
    assert result == True

def test_compR1_1_with_other_doc_types():
    instance = Instance(documentation=[
        Documentation(type='contact'), 
        Documentation(type='citation'), 
        Documentation(type='release'),
        Documentation(type='faq'),
        Documentation(type='support'),
        Documentation(type='installation'),
        Documentation(type='troubleshooting'),
        Documentation(type='privacy policy'),
        Documentation(type='disclaimer'),
        Documentation(type='api reference'),
        Documentation(type='getting started'),
        Documentation(type='tutorial'),
        Documentation(type='overview'),
        Documentation(type='specification'),
        Documentation(type='developer guide'),
        Documentation(type='maintainer guide')
    ])
    result, logs = compR1_1(instance)
    assert result == False

if __name__ == "__main__":
    pytest.main()

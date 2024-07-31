import pytest
from pydantic import BaseModel, AnyUrl
from typing import List, Optional
from app.models.instance import Documentation, Instance

from app.services.r_indicators import compR1_1

# Test cases
def test_compR1_1_with_usage_guide():
    instance = Instance(documentation=[Documentation(type='usage guide')])
    assert compR1_1(instance) == True

def test_compR1_1_with_license():
    instance = Instance(documentation=[Documentation(type='license')])
    assert compR1_1(instance) == False

def test_compR1_1_with_mixed_docs():
    instance = Instance(documentation=[
        Documentation(type='license'), 
        Documentation(type='usage guide')
    ])
    assert compR1_1(instance) == True

def test_compR1_1_with_no_guide_docs():
    instance = Instance(documentation=[
        Documentation(type='license'), 
        Documentation(type='terms of use')
    ])
    assert compR1_1(instance) == False

def test_compR1_1_with_empty_docs():
    instance = Instance(documentation=[])
    assert compR1_1(instance) == False

def test_compR1_1_with_none_docs():
    instance = Instance(documentation=None)
    assert compR1_1(instance) == False

def test_compR1_1_with_case_insensitive_check():
    instance = Instance(documentation=[Documentation(type='UsAgE GuIdE')])
    assert compR1_1(instance) == True

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
    assert compR1_1(instance) == False

if __name__ == "__main__":
    pytest.main()

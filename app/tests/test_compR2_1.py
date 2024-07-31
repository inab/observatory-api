import pytest
from pydantic import BaseModel, AnyUrl
from typing import List, Optional

from app.models.instance import Documentation, License, Instance

from app.services.r_indicators import compR2_1



# Test cases
def test_compR2_1_with_valid_documentation():
    instance = Instance(
        documentation=[Documentation(type='License')],
        license=[]
    )
    assert compR2_1(instance) == True

def test_compR2_1_with_valid_license():
    instance = Instance(
        documentation=[Documentation(type='Other Document')],
        license=[License(name='MIT', url='https://opensource.org/licenses/MIT')]
    )
    assert compR2_1(instance) == True

def test_compR2_1_with_no_license_and_no_relevant_documentation():
    instance = Instance(
        documentation=[Documentation(type='Other Document')],
        license=[License(name='Unlicensed', url='https://example.com')]
    )
    assert compR2_1(instance) == False

def test_compR2_1_with_valid_documentation_and_invalid_license():
    instance = Instance(
        documentation=[Documentation(type='Terms of Service')],
        license=[License(name='Unlicensed', url='https://example.com')]
    )
    assert compR2_1(instance) == True

def test_compR2_1_with_no_documentation_and_no_license():
    instance = Instance(
        documentation=[],
        license=[]
    )
    assert compR2_1(instance) == False

def test_compR2_1_with_partial_license_name():
    instance = Instance(
        documentation=[Documentation(type='Other Document')],
        license=[License(name='MIT', url='https://opensource.org/licenses/MIT')]
    )
    assert compR2_1(instance) == True

def test_compR2_1_with_documentation_variation():
    instance = Instance(
        documentation=[Documentation(type='End User License Agreement')],
        license=[]
    )
    assert compR2_1(instance) == True

def test_compR2_1_with_invalid_documentation():
    instance = Instance(
        documentation=[Documentation(type='News')],
        license=[License(name='Unknown', url='https://example.com')]
    )
    assert compR2_1(instance) == False
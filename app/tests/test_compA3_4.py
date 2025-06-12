import pytest

from app.services.a_indicators import compA3_4
from app.models.instance import Instance


def test_compA3_4_with_e_infrastructures():
    instance = Instance(type='cmd', e_infrastructures=['galaxy.eu'], links=[], source=[])
    result, logs = compA3_4(instance)
    assert result == True

'''
def test_compA3_4_with_e_infrastructure_links():
    instance = Instance(type='cmd', e_infrastructures=[], webpage=['https://vre.multiscalegenomics.eu/'], source=[])
    result, logs = compA3_4(instance)
    assert result ==  True
'''

def test_compA3_4_with_galaxy_source():
    instance = Instance(type='cmd', e_infrastructures=[], links=[], source=['galaxy'])
    result, logs = compA3_4(instance)
    assert result ==  True

def test_compA3_4_with_toolshed_source():
    instance = Instance(type='no_web', e_infrastructures=[], links=[], source=['toolshed'])
    result, logs = compA3_4(instance)
    assert result ==  True

def test_compA3_4_with_none_type():
    instance = Instance(type=None, e_infrastructures=[], links=[], source=[])
    result, logs = compA3_4(instance)
    assert result ==  False

def test_compA3_4_with_web_type_no_e_infrastructures():
    instance = Instance(type='web', e_infrastructures=[], links=[], source=[])
    result, logs = compA3_4(instance)
    assert result ==  False

def test_compA3_4_with_web_type_and_e_infrastructures():
    instance = Instance(type='web', e_infrastructures=['some_infrastructure'], links=[], source=[])
    result, logs = compA3_4(instance)
    assert result ==  False

def test_compA3_4_with_web_type_and_e_infrastructure_links():
    instance = Instance(type='web', e_infrastructures=[], webpage=['https://usegalaxy.eu'], source=[])
    result, logs = compA3_4(instance)
    assert result ==  False

def test_compA3_4_with_web_type_and_galaxy_source():
    instance = Instance(type='web', e_infrastructures=[], links=[], source=['galaxy'])
    result, logs = compA3_4(instance)
    assert result ==  False

if __name__ == "__main__":
    pytest.main()
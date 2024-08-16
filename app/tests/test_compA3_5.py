import pytest

from app.services.a_indicators import compA3_5
from app.models.instance import Instance

def test_compA3_5_with_multiple_e_infrastructures():
    instance = Instance(type='cmd', e_infrastructures=['infra1', 'infra2'], links=[], source=[])
    result, logs = compA3_5(instance)
    assert result == True

def test_compA3_5_with_multiple_e_infrastructure_links():
    instance = Instance(type='cmd', e_infrastructures=[], webpage=['https://vre.multiscalegenomics.eu/', 'https://usegalaxy.eu'], source=[])
    result, logs = compA3_5(instance)
    print(logs)
    assert result ==  True

def test_compA3_5_with_multiple_galaxy_toolshed_sources():
    instance = Instance(type='lib', e_infrastructures=[], links=[], source=['galaxy', 'toolshed'])
    result, logs = compA3_5(instance)
    assert result ==  True

def test_compA3_5_with_none_super_type():
    instance = Instance(type=None, e_infrastructures=[], links=[], source=[])
    result, logs = compA3_5(instance)
    assert result ==  False

def test_compA3_5_with_web_super_type_no_e_infrastructures():
    instance = Instance(type='web', e_infrastructures=[], links=[], source=[])
    result, logs = compA3_5(instance)
    assert result ==  False

def test_compA3_5_with_web_super_type_and_multiple_e_infrastructures():
    instance = Instance(type='rest', e_infrastructures=['galaxy.eu', 'infra2'], links=[], source=[])
    result, logs = compA3_5(instance)
    assert result ==  False

def test_compA3_5_with_web_super_type_and_multiple_e_infrastructure_links():
    instance = Instance(type='web', e_infrastructures=[], links=['https://vre.multiscalegenomics.eu/resource', 'https://usegalaxy.org/resource'], source=[])
    result, logs = compA3_5(instance)
    assert result == False

def test_compA3_5_with_web_super_type_and_multiple_galaxy_toolshed_sources():
    instance = Instance(type='web', e_infrastructures=[], links=[], source=['galaxy', 'toolshed'])
    result, logs = compA3_5(instance)
    assert result ==  False

def test_compA3_5_with_web_super_type_single_galaxy_source():
    instance = Instance(type='web', e_infrastructures=[], links=[], source=['galaxy'])
    result, logs = compA3_5(instance)
    assert result ==  False

if __name__ == "__main__":
    pytest.main()
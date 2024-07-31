import pytest

from app.services.a_indicators import compA3_5

class MockInstance:
    def __init__(self, super_type, e_infrastructures, links, source):
        self.super_type = super_type
        self.e_infrastructures = e_infrastructures
        self.links = links
        self.source = source

def test_compA3_5_with_multiple_e_infrastructures():
    instance = MockInstance(super_type='no_web', e_infrastructures=['infra1', 'infra2'], links=[], source=[])
    assert compA3_5(instance) == True

def test_compA3_5_with_multiple_e_infrastructure_links():
    instance = MockInstance(super_type='no_web', e_infrastructures=[], links=['https://vre.multiscalegenomics.eu/resource', 'https://usegalaxy.org/resource'], source=[])
    assert compA3_5(instance) == True

def test_compA3_5_with_multiple_galaxy_toolshed_sources():
    instance = MockInstance(super_type='no_web', e_infrastructures=[], links=[], source=['galaxy', 'toolshed'])
    assert compA3_5(instance) == True

def test_compA3_5_with_none_super_type():
    instance = MockInstance(super_type=None, e_infrastructures=[], links=[], source=[])
    assert compA3_5(instance) == False

def test_compA3_5_with_web_super_type_no_e_infrastructures():
    instance = MockInstance(super_type='web', e_infrastructures=[], links=[], source=[])
    assert compA3_5(instance) == False

def test_compA3_5_with_web_super_type_and_multiple_e_infrastructures():
    instance = MockInstance(super_type='web', e_infrastructures=['infra1', 'infra2'], links=[], source=[])
    assert compA3_5(instance) == True

def test_compA3_5_with_web_super_type_and_multiple_e_infrastructure_links():
    instance = MockInstance(super_type='web', e_infrastructures=[], links=['https://vre.multiscalegenomics.eu/resource', 'https://usegalaxy.org/resource'], source=[])
    assert compA3_5(instance) == True

def test_compA3_5_with_web_super_type_and_multiple_galaxy_toolshed_sources():
    instance = MockInstance(super_type='web', e_infrastructures=[], links=[], source=['galaxy', 'toolshed'])
    assert compA3_5(instance) == True

def test_compA3_5_with_web_super_type_single_galaxy_source():
    instance = MockInstance(super_type='web', e_infrastructures=[], links=[], source=['galaxy'])
    assert compA3_5(instance) == False

if __name__ == "__main__":
    pytest.main()
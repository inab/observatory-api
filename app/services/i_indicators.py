
from app.constants import VERIFIABLE_FORMATS, DEPENDENCIES_AWARE_SYSTEMS

def compI1_1(instance):
    '''Usage of standard data formats.'''
    inputs = instance.input if instance.input is not None else []
    outputs = instance.output if instance.output is not None else []
    return any(t.vocabulary for t in inputs + outputs)

def compI1_2(instance):
    '''API standard specification.'''
    documentation = instance.documentation if instance.documentation is not None else []
    return any(doc.type == 'API specification' for doc in documentation)


def compI1_3(instance):
    '''Verificability of data formats.'''

    inputs = instance.input if instance.input is not None else []
    outputs = instance.output if instance.output is not None else []

    terms = {i.term.lower() for i in inputs + outputs}
    return any(term in VERIFIABLE_FORMATS for term in terms)

def compI1_4(instance):
    '''
    Flexibility of data format supported.'''
    inputs = instance.input if instance.input is not None else []
    outputs = instance.output if instance.output is not None else []
    return len(inputs) > 1 and len(outputs) > 1

def compI2_1(instance):
    '''Existence of API/library version.'''
    return instance.type in ['lib', 'rest', 'soap', 'api']

def compI2_2(instance):
    '''E-infrastructure compatibility.'''
    if instance.source is None:
        return False
    return any(source in ['galaxy', 'toolshed'] for source in instance.source)

def compI3_1(instance):
    '''Dependencies statement.'''
    return bool(instance.dependencies)

def compI3_2(instance):
    '''Dependencies are provided.'''
    lowercase_systems = [system.lower() for system in DEPENDENCIES_AWARE_SYSTEMS]

    if any(source in ['toolshed', 'bioconda', 'bioconductor'] for source in instance.source):
        return True

    if any(registry.lower() in lowercase_systems for registry in instance.registries):
        return True

    return any(any(a in url for a in ['bioconda', 'bioconductor', 'galaxy']) for url in instance.links)


def compI3_3(instance):
    '''Dependency-aware system.'''
    return compI3_2(instance)

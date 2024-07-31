from app.constants import STRUCT_META, SOFT_REG

def compF1_2(instance):
    '''Semantic versioning'''
    if instance.version:
        parts = instance.version.split('.')
        if len(parts) < 2:
            return False
        for part in parts:
            if not part.isdigit():
                return False
        return True
    return False


def compF2_1(instance):
    '''Structured Metadata.'''
    if instance.source is None:
        return False
    return any(source in STRUCT_META for source in instance.source)

def compF2_2(instance):
    '''Software described using ontologies or controlled vocabularies.'''
    return any(t.vocabulary for t in instance.topics + instance.operations)


def compF3_1(instance):
    '''Searchability in registries.'''
    if instance.source is None:
        return False
    
    soft_reg_lower = [source.lower() for source in SOFT_REG]
    return any(source.lower() in soft_reg_lower for source in instance.source)

def compF3_2(instance):
    '''Searchability in software repositories.'''
    if instance.repository is None:
        return False
    return any(repo for repo in instance.repository if repo)

def compF3_3(instance):
    '''Searchability in literature.'''
    if instance.publication is None:
        return False
    return any(pub for pub in instance.publication if pub)
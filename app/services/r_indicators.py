from app.constants import NO_GUIDE, PERMISSIONS_TYPES
from app.models.instance import Instance, License

def compR1_1(instance):
    '''Existence of usage guides.'''
    if not instance.documentation:
        return False
    no_guide_lower = [doc.lower() for doc in NO_GUIDE]
    return any(all(doc_type not in doc.type.lower() for doc_type in no_guide_lower) for doc in instance.documentation)

def compR2_1(instance: Instance) -> bool:
    '''Existence of license.'''
    if any(doc.type.lower() in (d.lower() for d in PERMISSIONS_TYPES) for doc in (instance.documentation or [])):
        return True
    
    if instance.license:
        for lic in instance.license:
            license_name = lic.name if isinstance(lic, License) else lic

            if isinstance(license_name, str) and license_name.lower() not in ['unlicensed', 'unknown', 'unlicense']:
                return True
            
    return False

def compR2_2(instance):
    '''Technical conditions of use.'''
    return compR2_1(instance)

def compR3_1(instance):
    '''Contribution policy.'''
    return any(doc.type == 'contribution policy' for doc in instance.documentation)

def compR3_2(instance):
    '''Existence of credit.'''
    return bool(instance.authors)

def compR4_1(instance):
    '''Usage of (public) version control.'''
    return instance.version_control

def compR4_2(instance):
    '''Release Policy.'''
    return any(doc.type == 'release policy' for doc in instance.documentation)

from app.constants import DOWNLOADABLE_SOURCES, FREE_OS, E_INFRASTRUCTURES

def compA1_1(instance):
    '''Existence of API or web.'''
    return instance.operational is True

def compA1_2(instance):
    '''Existence of downloadable and buildable software working version.'''
    if instance.super_type == 'no_web':
        return bool(instance.download) or any(source in DOWNLOADABLE_SOURCES for source in instance.source)
    return False

def compA1_3(instance):
    '''Existence of installation instructions.'''
    if instance.super_type == 'no_web':
        has_install_instructions = any(doc.type == 'installation' for doc in instance.documentation)
        return bool(instance.download) or any(source in DOWNLOADABLE_SOURCES for source in instance.source) or has_install_instructions
    return False

def compA1_4(instance):
    '''Existence of test data.'''
    if instance.documentation is None:
        instance.documentation = []
    has_test_data_in_docs = any(doc.type == 'test data' for doc in instance.documentation)
    return bool(instance.test) or has_test_data_in_docs


def compA1_5(instance):
    '''Existence of software source code.'''
    return instance.super_type == 'no_web' and bool(instance.src)

def compA3_1(instance):
    '''Registration not compulsory.'''
    return instance.registration_not_mandatory is True

def compA3_2(instance):
    '''Availability of version for free OS.'''
    if instance.super_type == 'no_web':
        if instance.os is None:
            return False
        
        free_os_lower = [os.lower() for os in FREE_OS]
        return any(os.lower() in free_os_lower for os in instance.os)
    return True

def compA3_3(instance):
    '''Availability for several OS.'''
    if instance.super_type == 'no_web' and instance.os is not None:
        return len(instance.os) > 1
    return False

E_INFRASTRUCTURES = ['vre.multiscalegenomics.eu', 'galaxy.', 'usegalaxy.']

def compA3_4(instance):
    '''Availability on free e-Infrastructures.'''
    if instance.super_type == 'no_web' or instance.super_type == 'web':
        if instance.e_infrastructures:
            return True
        if instance.links:
            return any(any(e in url for e in E_INFRASTRUCTURES) for url in instance.links)
        if instance.source:
            return 'galaxy' in instance.source or 'toolshed' in instance.source
    return False


def compA3_5(instance):
    '''Availability on several e-Infrastructures.'''
    if instance.super_type == 'no_web' or instance.super_type == 'web':
        if instance.e_infrastructures and len(instance.e_infrastructures) > 1:
            return True
        if instance.links:
            count = sum(1 for url in instance.links if any(e in url for e in E_INFRASTRUCTURES))
            if count > 1:
                return True
        if instance.source:
            return len([s for s in instance.source if s in ['galaxy', 'toolshed']]) > 1
    return False
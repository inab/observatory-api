import logging
from typing import Tuple
from app.constants import STRUCT_META, SOFT_REG
from app.services.utils import *

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def compF1_2(instance) -> Tuple[bool, str]:
    '''Semantic versioning'''
    print('Computing F1.2')
    logs = []
    recommendation = []
    recommendation.append("Aligning with semantic versioning involves adopting the MAJOR.MINOR.PATCH format, using pre-release labels and build metadata, and maintaining consistency in version increments. By clearly documenting your versioning practices and using tools to manage versions, you can improve version management and make your software easier to maintain and use.") 
    
    if instance.version:
        logs.append(f"⚙️ Checking if version '{instance.version}' follows semantic versioning standards.")
        logs = log_version(instance, logs)
        
        # remove any leading 'v' from the version
        if instance.version.lower().startswith('v'):
            instance.version = instance.version[1:]

        parts = instance.version.split('.')
        
        if len(parts) < 2:
            logs.append("❌ Version does not have enough parts (should be at least MAJOR.MINOR).")
            logs.append("Result: FAILED")
            return False, logs
        
        for part in parts:
            if not part.isdigit():
                logs.append(f"❌ Part '{part}' is not a digit.")
                logs.append("Result: FAILED")
                return False, logs
        
        logs.append("✅ Version is valid.")
        logs.append("Result: PASSED")
        recommendation = [] 
        return True, logs
    
    logs.append("❌ No version provided.")
    logs.append("Result: FAILED")
    return False, logs


def compF2_1(instance) -> Tuple[bool, str]:
    '''Structured Metadata.'''

    print('Computing F2.1')

    logs = []
    logs.append(f"⚙️ Checking if any source provides structured metadata.")
    logs = log_sources(instance, logs)

    if not instance.source:
        logs.append("❌ Source is empty.")
        logs.append("Result: FAILED")
        return False, logs

    logs.append(f"⚙️ Comparing sources against: ")

    for source in instance.source:
        if source in STRUCT_META:
            logs.append(f"✅ Source '{source}' provides structured metadata.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append(f"❌ Source '{source}' does not provide structured metadata.")
    
    logs.append("❌ No sources provide structured metadata.")
    logs.append("Result: FAILED")
    return False, logs

def compF2_2(instance) -> Tuple[bool, str]:
    '''Software described using ontologies or controlled vocabularies.'''

    print('Computing F2.2')

    logs = []
    
    logs.append("⚙️ Verifying whether a topic or operation is part of a specific ontology or controlled vocabulary.")

    logs = log_topics_operations(instance, logs)

    if instance.topics:
        logs.append(f"⚙️ Checking if any topic is part of an ontology or controlled vocabulary.")
        for topic in instance.topics:
            if topic.vocabulary:
                logs.append(f"✅ Topic '{topic.term}' is part of the '{topic.vocabulary}' ontology or controlled vocabulary.")
                logs.append("Result: PASSED")
                return True, logs
            else:
                logs.append(f"❌ Topic '{topic.term}' is not part of any ontology or controlled vocabulary.")

    if instance.operations:
        logs.append(f"⚙️ Checking if any operation is part of an ontology or controlled vocabulary.") 
        for operation in instance.operations:
            if operation.vocabulary:
                logs.append(f"✅ Operation '{operation.term}' is part of the '{operation.vocabulary}' ontology or controlled vocabulary.")
                logs.append("Result: PASSED")
                return True, logs
            else:
                logs.append(f"❌ Operation '{operation.term}' is not part of any ontology or controlled vocabulary.")

    
    logs.append("❌ No topic or operation involves the use of ontologies or controlled vocabularies.")
    logs.append("Result: FAILED")
    return False, logs

def compF3_1(instance) -> Tuple[bool, str]:
    '''Searchability in registries.'''

    print('Computing F3.1')

    logs = []

    logs.append(f"⚙️ Checking if any source matches software registries.")
    logs = log_sources(instance, logs)

    if instance.source is None:
        logs.append("❌ No source provided. Checking registries...")
    else:
        sources_registries = ['biotools', 'bioconda', 'bioconductor', 'toolshed', 'sourceforge']
        soft_reg_lower = [source.lower() for source in sources_registries]
        logs.append(f" ⚙️ Comparing sources against: {sources_registries}")
        
        for source in instance.source:
            if source.lower() in soft_reg_lower:
                logs.append(f"✅ Source '{source}' matches software registries.")
                logs.append("Result: PASSED")
                return True, logs
            
        logs.append(f"❌ No source matches software registries. Checking registries ...")

    logs.append(f"⚙️ Checking if the specified software registry matches any of the known registries.")
    logs = log_registries(instance, logs)

    if instance.registries is None:
        logs.append("❌ No registries.")
        logs.append("Result: FAILED")
        return False, logs

    else:
        logs.append(f"⚙️ Comparing registries against: ")
        soft_reg_lower = [source.lower() for source in SOFT_REG]
        for registry in instance.registries:
            if registry.lower() in soft_reg_lower:
                logs.append(f"✅  Registry '{registry}' matches software registries.")
                logs.append("Result: PASSED")
                return True, logs
            
        logs.append(f"❌ No registry matches software registries.")
        logs.append("Result: FAILED")
        return False, logs


def compF3_2(instance) -> Tuple[bool, str]:
    '''Searchability in software repositories.
    GitHub, GitLab or Bitbucket
    '''

    print('Computing F3.2')

    logs = []
    
    logs.append(f"⚙️ Checking if any repository is an operational software repository.")
    logs = log_repositories(instance, logs)

    if not instance.repository:
        logs.append("❌ No repository.")
        logs.append("Result: FAILED")
        return False, logs
    
    if any(is_url_operational(repo) for repo in instance.repository if repo):
        logs.append("✅ At least one valid repository found.")
        logs.append("Result: PASSED")
        return True, logs
    
    logs.append("❌ No valid repositories found.")
    logs.append("Result: FAILED")
    return False, logs


def compF3_3(instance) -> Tuple[bool, str]:
    '''Searchability in literature.'''

    print('Computing F3.3')
    
    logs = []
    
    logs.append(f"⚙️ Checking if any publication is a valid publication.")
    logs = log_publications(instance, logs)

    if not instance.publication:
        logs.append("❌ No publication.")
        logs.append("Result: FAILED")
        return False, logs
    
    n_pubs = len([pub for pub in instance.publication if pub])
    if n_pubs > 0:
        logs.append(f"✅ {n_pubs} valid publication found.")
        logs.append("Result: PASSED")
        return True, logs
    
    logs.append("❌ No valid publications found.")
    logs.append("Result: FAILED")
    return False, logs

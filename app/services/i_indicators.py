import logging
from typing import List, Tuple
from app.constants import VERIFIABLE_FORMATS, DEPENDENCIES_AWARE_SYSTEMS, E_INFRASTRUCTURES, E_INFRASTRUCTURES_SOURCES
from app.services.utils import *

def compI1_1(instance) -> Tuple[bool, List[str]]:
    '''Usage of standard data formats.'''
    logs = []

    # Check if any of the inputs or outputs have a standard vocabulary
    logs.append("⚙️ Checking if any of the inputs or outputs use a standard data format.")
    
    inputs = instance.input or []
    outputs = instance.output or []
    # inputs and outputs each in a line logs
    logs = log_inputs_outputs(instance, logs)

    has_standard_format = any(t.vocabulary for t in inputs + outputs)
    for input in inputs:
        if input.vocabulary:
            logs.append(f"✅ Input '{input.term}' uses a standard data format '{input.vocabulary}'.")
        else:
            logs.append(f"❌ Input '{input.term}' does not use a standard data format.")
    for output in outputs:
        if output.vocabulary:
            logs.append(f"✅ Output '{output.term}' uses a standard data format '{output.vocabulary}'.")
        else:
            logs.append(f"❌ Output '{output.term}' does not use a standard data format.")
    
    if has_standard_format:
        logs.append("✅ At least one input or output uses a standard data format.")
        logs.append("Result: PASSED")
        return True, logs

    else:
        logs.append("❌ No standard data formats found in inputs or outputs.")
        logs.append("Result: FAIL")
        return False, logs


def compI1_2(instance) -> Tuple[bool, List[str]]:
    '''API standard specification.'''
    logs = []
    super_type = instance.super_type
    if super_type == 'no_web':
        logs.append('This is not a web-based software. This indicator is not applicable.')
        return False, logs
    
    # Check if any documentation entry is of type 'API specification'
    logs.append("⚙️ Checking if any documentation entry is an API specification and the url is operational.")
    documentation = instance.documentation or []
    logs = log_documentation(instance, logs)

    api_spec_found = False
    for doc in documentation:
        if doc.type.lower() == 'api specification':
            api_spec_found = True
            if is_url_operational(doc.url):
                logs.append("✅ API specification found in documentation and the URL is operational.")
                logs.append("Result: PASSED")
                return True, logs
            logs.append(f"❌ API specification found in documentation but the URL is not operational. URL: {doc.url}.")

    if api_spec_found:
        logs.append("❌ API specification found in documentation but the URL is not operational.")
        logs.append("Result: FAILED")
        return False, logs

    logs.append("❌ No API specification found in documentation.")
    logs.append("Result: FAIL")
    return False, logs

def compI1_3(instance) -> Tuple[bool, List[str]]:
    '''Verificability of data formats.'''
    logs = []
    
    # Check if any term is in the list of verifiable formats
    logs.append("⚙️ Checking if any data format is verifiable.")
    inputs = instance.input or []
    outputs = instance.output or []
    logs = log_inputs_outputs(instance, logs)
  
    # Collect terms from inputs and outputs
    terms = {i.term for i in inputs + outputs}

    logs.append(f"Formats considered verifiable: https://observatory.openebench.bsc.es/api/lists/verifiable_formats")
    logs.append(f"Formats found: {terms}")

    terms_lower = [ term.lower() for term in terms ]
    
    verifiable = False
    for term in terms_lower:
        if term in VERIFIABLE_FORMATS:
            logs.append(f"✅ Data format '{term}' is verifiable.")
            verifiable = True
        else:
            logs.append(f"❌ Data format '{term}' is not verifiable.")
        
    if verifiable:
        logs.append("✅ At least one data format is verifiable.")
        logs.append("Result: PASSED")
        return True, logs
    else:
        logs.append("❌ No verifiable data formats found.")
        logs.append("Result: FAILED")
        return False, logs


def compI1_4(instance) -> Tuple[bool, List[str]]:
    '''
    Flexibility of data format supported.
    '''
    logs = []

    logs.append("⚙️ Checking if more than one input and output data formats are supported.")
    # Check if there are more than one input and output formats
    inputs = instance.input or []
    outputs = instance.output or []
    logs = log_inputs_outputs(instance, logs)

    has_flexibility = len(inputs) > 1 and len(outputs) > 1
    if has_flexibility:
        logs.append("✅ More than one input and output data formats found.")
        logs.append("Result: PASSED")
        return True, logs

    else:
        logs.append("❌ Less than one input or output data formats found.")
        logs.append("Result: FAILED")
        return False, logs


def compI2_1(instance) -> Tuple[bool, List[str]]:
    '''Existence of API/library version.'''
    logs = []
    
    logs.append("⚙️ Checking if the instance type is one of the valid options (lib, rest, soap, or api).")
    # Check if the type is one of the valid options
    logs = log_type(instance, logs)

    has_valid_type = instance.type in ['lib', 'rest', 'soap', 'api']
    if has_valid_type:
        logs.append("✅ Instance type is valid.")
        logs.append("Result: PASSED")
        return True, logs
    
    logs.append("❌ Instance type is not valid.")
    logs.append("Result: FAILED")
    return False, logs


def compI2_2(instance) -> Tuple[bool, List[str]]:
    '''E-infrastructure compatibility.'''
    logs = []

    # Checking if at least one e-infrastructure is available
    logs.append("⚙️ Checking if at least one e-infrastructure is available")
    e_infrastructures_data = instance.e_infrastructures or []
    logs.append(f"🔍 Received e-infrastructures: {e_infrastructures_data}")

    if e_infrastructures_data:
        if len(e_infrastructures_data) >= 1:
            logs.append("✅ At least one e-infrastructure is available.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append("❌ No e-infrastructures available. Checking links ...")
    
    else:
        logs.append("❌ No e-infrastructures provided. Checking links ...")

    logs.append("⚙️ Checking if at least one e-infrastructure is referenced in the links and the link is operational")
    logs.append("Considered e-infrastructures: https://observatory.openebench.bsc.es/api/lists/e_infrastructures")

    webpage = instance.webpage or []

    logs = log_webpages(instance, logs)

    # Checking if at least one e-infrastructure is referenced in the links and is operational
    if webpage:
        n_operational = 0
        for url in webpage:
            if any(e in str(url) for e in E_INFRASTRUCTURES):
                is_operational = is_url_operational(url)
                if is_operational:
                    logs.append(f"✅ E-infrastructure '{url}' is operational.")
                    n_operational += 1
                else:
                    logs.append(f"❌ E-infrastructure '{url}' is not operational.")
        if n_operational >= 1:
            logs.append("✅ At least one operational e-infrastructure is referenced in the links.")
            logs.append("Result: PASS")
            return True, logs
        else:
            logs.append("❌ No operational e-infrastructures referenced in the links. Checking sources ...")
    
    else:
        logs.append("❌ No links provided. Cheking sources ...")

    logs.append("⚙️ Checking if at least one e-infrastructure is referenced in the source")
    source_data = instance.source or []
    logs = log_sources(instance, logs)

    # Checking if at least one e-infrastructure is referenced in the source
    if source_data:
        e_infrastructures_referenced = [source for source in source_data if source in E_INFRASTRUCTURES_SOURCES]
        if len(e_infrastructures_referenced) >= 1:
            logs.append("✅ At least one e-infrastructure is referenced in the source.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append("❌ No e-infrastructures referenced in the source.")
    
    else:
        logs.append("❌ No sources provided.")
    
    logs.append("Result: FAILED")
    return False, logs


def compI3_1(instance) -> Tuple[bool, List[str]]:
    '''Dependencies statement.'''
    logs = []
    
    logs.append("⚙️ Checking if dependencies are stated.")
    dependencies = instance.dependencies or []

    logs = log_dependencies(instance, logs)

    has_dependencies = bool(dependencies)
    if has_dependencies:
        logs.append("✅ Dependencies found.")
        logs.append("Result: PASSED")
        return True, logs
    
    logs.append("❌ No dependencies found.")
    logs.append("Result: FAILED")
    return False, logs

def compI3_2(instance) -> Tuple[bool, List[str]]:
    '''Dependencies are provided.'''
    logs = []
    
    lowercase_systems = [system.lower() for system in DEPENDENCIES_AWARE_SYSTEMS]
    
    logs.append("⚙️ Checking if dependencies are provided through dependencies-aware systems.")
    logs.append(f"Considered systems: https://observatory.openebench.bsc.es/api/lists/dependencies_aware_systems")
    logs.append("Checking registries, links, and sources.")

    logs = log_sources(instance, logs)
    logs = log_registries(instance, logs)
    logs = log_links(instance, logs)    

    sources = instance.source or []
    registries = instance.registries or []
    links = instance.links or []
    
    # Check sources
    if any(source in ['toolshed', 'bioconda', 'bioconductor'] for source in sources):
        logs.append("✅ Dependencies-aware system identified in sources.")
        logs.append("Result: PASSED")
        return True, logs
    
    # Check registries
    if any(registry.lower() in lowercase_systems for registry in registries):
        logs.append("✅ Dependencies-aware system identified in registries.")
        logs.append("Result: PASSED")
        return True, logs

    # Check links
    if any(any(a in url for a in ['bioconda', 'bioconductor', 'galaxy']) for url in links):
        logs.append("✅ Dependencies-aware system identified in links.")
        logs.append("Result: PASSED")
        return True, logs

    logs.append("❌ No dependencies-aware system identified.")
    logs.append("Result: FAILED")
    return False, logs

def compI3_3(instance):
    '''Dependency-aware system.'''
    result, logs = compI3_1(instance)
    return result, logs

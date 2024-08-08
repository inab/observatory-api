import requests
from typing import List
from app.models.instance import Instance
import requests
from typing import Optional

def is_url_operational(url: str, timeout: int = 5) -> bool:
    '''
    Check if a URL is operational by performing a HEAD request.

    Args:
        url (str): The URL to check.
        timeout (int, optional): The timeout for the request in seconds. Defaults to 5.
    Returns:
        bool: True if the URL is operational, False otherwise.
    '''
    try:
        # Perform a HEAD request to check if the URL is reachable
        response = requests.head(url, timeout=timeout)

        # Check if the response status code is in the range of 200-299
        if response.status_code >= 200 and response.status_code < 300:
            return True  # URL is operational
        else:
            print(f"URL responded with status: {response.status_code}")
            return False  # URL is not operational
    except requests.RequestException as e:
        print(f"Error checking URL: {e}")
        return False  # URL is not operational

def log_version(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the version of the Instance.

    Args:
        Instance (Instance): The Instance object containing the version.
        logs (list[str]): A list to store the logs.

    Returns:
        list[str]: A list containing the logs.

    '''
    if Instance.version:
        logs.append(f"🔍 Version provided: {Instance.version}")
    else:
        logs.append("🔍 No version provided.")
    
    return logs

def log_sources(Instance, logs):
    '''Log the sources of the Instance.'''
    if Instance.source:
        logs.append(f"🔍 Sources provided: {Instance.source}")
    else:
        logs.append("🔍 No sources provided.")
    
    return logs



def build_dict_items_log(dict_items: list[dict]) -> list[str]:
    '''Build a log string for a list of dictionaries.
    
    Args:
        dict_items (list[dict]): The list of dictionaries to build the log string for.
    
    Returns:
        list[str]: The log string for the list of dictionaries.
    '''
    log = []
    for item in dict_items:
        one_liner = ""
        item = item.__dict__
        for key, value in item.items():
            one_liner += f"{key}: {value}, "
        
        log.append(one_liner)
    
    return log



def log_topics_operations(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the topics and operations of the Instance.

    Args:
        Instance (Instance): The Instance object containing topics and operations.
        logs (list[str]): A list to store the logs.

    Returns:
        list[str]: A list containing the logs.

    '''
    if Instance.topics:
        logs.append("🔍 Topics provided:")
        topics_log = build_dict_items_log(Instance.topics)
        logs.extend(topics_log)
    else:
        logs.append("🔍 No topics provided.")
    
    if Instance.operations:
        logs.append("🔍 Operations provided:")
        operations_log = build_dict_items_log(Instance.operations)
        logs.extend(operations_log)
    else:
        logs.append("🔍 No operations provided.")
    
    return logs





def log_list_strings(string_list: List[str]) -> List[str]:
    '''Log a list of strings.

    Args:
        string_list (List[str]): The list of strings to be logged.

    Returns:
        List[str]: The logged list of strings, with each string prefixed by a hyphen.
    '''
    log = []
    for item in string_list:
        log.append(f"- {item}")
    
    return log
    


def log_registries(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the registries of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the registries.
        logs (list[str]): The list of logs to append the registry information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.registries:
        logs.append(f"🔍 Registries provided:")
        registries_log = log_list_strings(Instance.registries)
        logs.extend(registries_log)
    else:
        logs.append("🔍 No registries provided.")
    
    return logs


def log_repositories(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the repositories of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the repositories.
        logs (list[str]): The list of logs to append the repository information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.repository:
        logs.append(f"🔍 Repositories provided:")
        repositories_log = log_list_strings(Instance.repository)
        logs.extend(repositories_log)
    else:
        logs.append("🔍 No repositories provided.")
    
    return logs



def log_pub_identifiers_title(publications: List[dict]) -> List[str]:
    '''
    Log the identifiers and title of the publications.

    Parameters:
        publications (List[dict]): The list of publications.

    Returns:
        List[str]: The logged list of identifiers and title.

    '''
    log = []
    for pub in publications:
        log.append(f"Title: {pub.get('title')}, DOI: {pub.get('doi')}, PMID: {pub.get('pmid')}, PMCID: {pub.get('pmcid')}")
    
    return log


def log_publications(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the publications of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the publications.
        logs (list[str]): The list of logs to append the publication information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.publication:
        logs.append(f"🔍 Publications provided:")
        publications_log = log_pub_identifiers_title(Instance.publication)
        logs.extend(publications_log)
    else:
        logs.append("🔍 No publications provided.")
    
    return logs

def log_webpages(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the webpages of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the webpages.
        logs (list[str]): The list of logs to append the webpage information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.webpage:
        logs.append(f"🔍 Webpages provided:")
        webpages_log = log_list_strings(Instance.webpage)
        logs.extend(webpages_log)
    else:
        logs.append("🔍 No webpages provided.")
    
    return logs


def log_downloads(downloads: list, logs: list[str]) -> list[str]:
    '''
    Log the downloads of the Instance.

    Parameters:
        downloads (list): The list of downloads.
        logs (list[str]): The list of logs to append the download information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if downloads:
        logs.append(f"🔍 Downloads provided:")
        downloads_log = log_list_strings(downloads)
        logs.extend(downloads_log)
    else:
        logs.append("🔍 No downloads provided.")
    
    return logs


def log_documentation(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the documentation of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the documentation.
        logs (list[str]): The list of logs to append the documentation information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.documentation:
        logs.append(f"🔍 Documentation provided:")
        documentation_log = build_dict_items_log(Instance.documentation)
        logs.extend(documentation_log)
    else:
        logs.append("🔍 No documentation provided.")
    
    return logs

def log_test_data_URLs(Instance: Instance, logs:list[str]) -> list[str]:
    '''
    Log the test data URLs of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the test data URLs.
        logs (list[str]): The list of logs to append the test data URL information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.test:
        logs.append(f"🔍 Test data URLs provided:")
        test_log = log_list_strings(Instance.test)
        logs.extend(test_log)
    else:
        logs.append("🔍 No test data URLs provided.")
    
    return logs


def log_src_URLs(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the source URLs of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the source URLs.
        logs (list[str]): The list of logs to append the source URL information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.src:
        logs.append(f"🔍 Source URLs provided:")
        src_log = log_list_strings(Instance.src)
        logs.extend(src_log)
    else:
        logs.append("🔍 No source URLs provided.")
    
    return logs


def log_inputs_outputs(Instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the inputs and outputs of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the inputs and outputs.
        logs (list[str]): The list of logs to append the input and output information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if Instance.input:
        logs.append(f"🔍 Inputs provided:")
        inputs_log = build_dict_items_log(Instance.input)
        logs.extend(inputs_log)
    else:
        logs.append("🔍 No inputs provided.")
    
    if Instance.output:
        logs.append(f"🔍 Outputs provided:")
        outputs_log = build_dict_items_log(Instance.output)
        logs.extend(outputs_log)
    else:
        logs.append("🔍 No outputs provided.")
    
    return logs

def log_dependencies(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the dependencies of the Instance.

    Parameters:
        instance (Instance): The Instance containing the dependencies.
        logs (list[str]): The list of logs to append the dependency information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.dependencies:
        logs.append(f"🔍 Dependencies provided:")
        dependencies_log = log_list_strings(instance.dependencies)
        logs.extend(dependencies_log)
    else:
        logs.append("🔍 No dependencies provided.")
    
    return logs


def log_links(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the links of the Instance.

    Parameters:
        instance (Instance): The Instance containing the links.
        logs (list[str]): The list of logs to append the link information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.links:
        logs.append(f"🔍 Links provided:")
        links_log = log_list_strings(instance.links)
        logs.extend(links_log)
    else:
        logs.append("🔍 No links provided.")
    
    return logs

def log_type(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the type of the Instance.

    Parameters:
        instance (Instance): The Instance containing the type.
        logs (list[str]): The list of logs to append the type information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.type:
        logs.append(f"🔍 Type provided: {instance.type}")
    else:
        logs.append("🔍 No type provided.")
    
    return logs


def log_e_infrastructues(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the e-infrastructures of the Instance.

    Parameters:
        instance (Instance): The Instance containing the e-infrastructures.
        logs (list[str]): The list of logs to append the e-infrastructures information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.e_infrastructures:
        logs.append(f"🔍 E-infrastructures provided:")
        e_infrastructures_log = log_list_strings(instance.e_infrastructures)
        logs.extend(e_infrastructures_log)
    else:
        logs.append("🔍 No e-infrastructures provided.")
    
    return logs

def log_os(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the operating systems of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the operating systems.
        logs (list[str]): The list of logs to append the operating system information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.os:
        logs.append(f"🔍 Operating systems provided:")
        os_log = log_list_strings(instance.os)
        logs.extend(os_log)
    else:
        logs.append("🔍 No operating systems provided.")
    
    return logs

def log_licenses(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the licenses of the Instance.

    Parameters:
        instance (Instance): The Instance containing the licenses.
        logs (list[str]): The list of logs to append the license information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.license:
        logs.append(f"🔍 Licenses provided:")
        license_log = build_dict_items_log(instance.license)
        logs.extend(license_log)
    else:
        logs.append("🔍 No licenses provided.")
    
    return logs


def log_authors(instance: Instance, logs: list[str]) -> list[str]:
    '''
    Log the authors of the Instance.

    Parameters:
        Instance (Instance): The Instance containing the authors.
        logs (list[str]): The list of logs to append the author information to.

    Returns:
        list[str]: The updated list of logs.

    '''
    if instance.authors:
        logs.append(f"🔍 Authors provided:")
        authors_log = build_dict_items_log(instance.authors)
        logs.extend(authors_log)
    else:
        logs.append("🔍 No authors provided.")
    
    return logs
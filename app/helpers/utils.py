import re
from functools import wraps
import warnings
import time
from pathlib import Path
from bson import ObjectId


from app.helpers.EDAM_forFE import EDAMDict


def attribute_check_and_set(instance, key, value, default_name='fairsoft_default_name', default_value=None):
    '''Check if the attribute is set. If it is not, set default attribute to the instance and raise a warning.'''
    if value == 'fairsoft_default':
        warnings.warn(f'Instance {key} not specified. Setting instance.{key} = None')
        setattr(instance, key, None)
    elif value == default_name:
        warnings.warn(f'Instance {key} not specified. Assigning default value "{default_name}"', Warning)
        setattr(instance, key, default_name)
    else:
        setattr(instance, key, value)

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


########
# Tool preparation functions
# These functions prepare the tool metadata to be displayed in the UI
#######

def get_pub(object_id):
    from app.helpers.database import connect_DB

    tools_collection, stats, pubs_collection = connect_DB()

    publication = pubs_collection.find_one({"_id": object_id})    
    if publication:
        return publication.get('data')
    else:
        return None

def prepareToolMetadata(entry):

    publications_records = set()

    publications_new = []
    if entry.get('publication'):
        for pub in entry['publication']:
            publication = get_pub(ObjectId(pub))
            if publication:
                publications_records.add(id)
                if 'citations' in publication:
                    del publication['citations']
                if 'abstract' in publication:
                    del publication['abstract']
            
                publications_new.append(publication)
        
    entry['publication'] = publications_new

    if entry.get('type'):
        if len(entry.get('type', []))>1:
            entry['other_types'] = entry.get('type', [])[1:]
            entry['type'] = entry.get('type', [])[0]
        else:
            entry['other_types'] = []
            entry['type'] = entry.get('type', [])[0]
    else:
        entry['type'] = None
        entry['other_types'] = []

    if entry.get('version'):
        if len(entry.get('version', []))>1:
            entry['other_versions'] = entry.get('version', [])[1:]
            entry['version'] = entry.get('version', [])[0]
        else:
            entry['other_versions'] = []
            entry['version'] = entry.get('version', [])[0]
    else:
        entry['version'] = None
        entry['other_versions'] = []


    if entry['authors'] is None:
        entry['authors'] = []
    else:
        for author in entry['authors']:
            if author['type'] == None:
                author['type'] = 'unknown'
            if author['name'] == None:
                author['name'] = 'unknown'
            if author['email'] == None:
                author['email'] = ''


    repos = []
    if entry['repository']:
        for repo in entry['repository']:
            if repo.get('url'):
                repos.append(repo['url'])
    entry['repository'] = repos

    if entry['test'] is True:
        entry['test'] = ['https://openebech.bsc.es']
    else:
        entry['test'] = []

    if entry['source_code']:
        entry['src'] = entry['source_code']
    else:
        entry['src'] = []
    entry.pop('source_code')


    if entry['operating_system']:
        entry['os'] = entry['operating_system']
    else:
        entry['os'] = []
    entry.pop('operating_system')

    return entry



def prepareLabel(tool):
    '''
    Keep only the label with uppercase letter if it exists
    '''
    def hasUpper(string):
        for letter in string:
        
            # checking for uppercase character and flagging
            if letter.isupper():
                res = True
                return True
        
        return False

    for label in tool['label']:
        if hasUpper(label):
            # put first in labels. LAbels is list to keep backwards compatibility
            tool['label'] = [label]
            break
    
    return tool
    

def prepareTopicsOperations(metadata, field, new_field):
    '''
    Prepares the topics and operations fields of a tool to be displayed in the UI
    field is the field to be processed (edam_topics or edam_operations)
    Example of processed field:
    [
        {
            "vocabulary": "EDAM",
            "term": "Topic",
            "uri": "http://edamontology.org/topic_0003"
        },
        ...
    ]
    
    '''
    items = metadata[field]
    new_items = []
    # look up for each item in the list the corresponding label
    for item in items:
        term = EDAMDict.get(item)
        if item:
            item = {
                'vocabulary': 'EDAM',
                'term': term,
                'uri': item
            }
            new_items.append(item)
    
    metadata[new_field] = new_items
    return metadata

def prepareDocumentation(metadata):
    '''
    Prepares the documentation field of a tool to be displayed in the UI
    Example of processed field:
    [
        {
            "type": "documentation",
            "url": "https://bio.tools/api/tool/blast2go/docs/1.0.0"
        },
        ...
    ]
    
    '''
    def match_url(string):
        # either http or https
        pattern = re.compile(r'https?://\S+')
        if pattern.match(string):
            return True
        else:
            return False

    def clean_documentation(documentation):
        '''
        Removes the documentation items that are not urls
        '''
        new_documentation = []
        for item in documentation:
            new_item = []
            if type(item[1])==str:
                if match_url(item[1]):
                    if item[0] == 'documentation':
                        new_item.append('general')
                    else:
                        new_item.append(item[0])
                    new_item.append(item[1])
                    new_documentation.append(new_item)

        return new_documentation

    items = clean_documentation(metadata['documentation'])
    new_items = []
    # look up for each item in the list the corresponding label
    for item in items:
        item = {
            'type': item[0],
            'url': item[1]
        }
        new_items.append(item)
    
    metadata['documentation'] = new_items
    return metadata


def prepareDataFormats(metadata, field):
    '''
    Prepares the input and output field of a tool to be displayed in the UI
    Example of processed field:
    [
        {   "vocabulary": "EDAM",
            "term": "Sequence format",
            "uri": "http://edamontology.org/format_1929",
            datatype: {
                "vocabulary": "EDAM",
                "term": "Sequence",
                "uri": "http://edamontology.org/data_0006"
            }
        },
        ...
    ]
    
    '''
    items = metadata[field]
    new_items = []
    # look up for each item in the list the corresponding label
    #print(items)
    for item in items:
        if 'datatype' in item:
            datatype = {
                'vocabulary': 'EDAM',
                'term': EDAMDict[item['datatype']],
                'uri': item['datatype']
            }
        else:
            datatype = {}

        # fix this ugly hack later
        if 'format' in item:
            format = {
                'vocabulary': '',
                'term': item['format']['term'],
                'uri': item['format']['uri'],
            }
            new_items.append(format)
        else:
            for format in item['formats']:
                if datatype:
                    format = {
                        'vocabulary': 'EDAM',
                        'term': EDAMDict[format],
                        'uri': format,
                        'datatype': datatype
                    }
                else:
                    format = {
                        'vocabulary': 'EDAM',
                        'term': EDAMDict[format],
                        'uri': format
                    }
                new_items.append(format)
    
    metadata[field] = new_items
    
    return metadata

def prepareListsIds(metadata):
    '''
    Add ids to a list of terms. 
    The ids are needed for v-for loops to keep proper track of items.
    See: https://stackoverflow.com/questions/44531510/why-not-always-use-the-index-as-the-key-in-a-vue-js-for-loop/75175749#75175749 
    fields: tool metadata fields that we need to add ids to.
    From:
    [
        term1,
        term2,
        ...
    ]
    To:
    [
        { term: term1, id: id1 },
        { term: term2, id: id2 },
        ...
    ]
    '''

    fields = [
        'edam_topics',
        'edam_operations',
        'documentation',
        'description',
        'webpage',
        'license',
        'links',
        'topics',
        'operations',
        'input',
        'output',
        'repository',
        'dependencies',
        'authors',
        'publication',
        'src',
        'os'
    ]

    #print(metadata)
    for field in fields:
        #print(f'Adding ids to field: {field}')
        new_list = [] 
        i=0
        if metadata.get(field):
            for item in metadata.get(field):
                new_item ={
                    'term': item,
                    'id': i
                }
                new_list.append(new_item)
                i+=1

            metadata[field] = new_list
    
    return metadata


################
# Prepare metadata for evaluation
################

def prepareMetadataForEvaluation(metadata):
    '''
    Reverts the kind of processing done in prepareListsIds
    From:
    [
        { term: term1, id: id1 },
        { term: term2, id: id2 },
        ...
    ] 
    
    To:
    [
        term1,
        term2,
        ...
    ]
    '''

    fields = [
        'edam_topics',
        'edam_operations',
        'documentation',
        'description',
        'license',
        'links',
        'input',
        'output',
        'repository',
        'dependencies',
        'os',
        'src',
        'authors',
        'publication',
        'topics', # added by prepareTopicsOperations
        'operations', # added by prepareTopicsOperations
        'webpage' # added by getWebPage
    ]

    for field in fields:
        print('preparing field: ', field)
        new_list = [] 
        for item in metadata[field]:
            new_item = item['term']
            new_list.append(new_item)
        
        metadata[field] = new_list

    return metadata


################
# Prepare name-type-label
################

def keep_first_label(tool):
    '''
    Processes a tool to turn a list of labels into a single label (index=0)
    '''
    if tool['data']['label']:
        tool['data']['label'] = tool['data']['label'][0]
    else:
        tool['data']['label'] = tool['data']['name']

    if len(tool["data"]["type"])>0:
        tool["data"]["types"] = tool['data']['type']
        tool['data']['type'] = tool['data']['type'][0]
        
    elif len(tool["data"]["type"])==0:
        tool["data"]["types"] = []
        tool['data']['type'] = "unknown"
        
    return tool['data']


##############
# sources_labels
##############

def find_github_repo(link):
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?github\.com\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None

def find_bioconductor_link(link):
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?bioconductor\.org\/packages\/[A-Za-z0-9_-]+\/bioc\/html\/[A-Za-z0-9_-]+')
    x = re.search(regex, link)
    if x:
        return x.group(0) + '.html'
    else:
        return None

def find_bitbucket_repo(link):
    '''
    Find Bitbuket repository in URL string
    '''
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?bitbucket\.org\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None

def find_galaxy_instance(link):
    '''
    Find Galaxy instance in URL string
    '''
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?usegalaxy\.eu')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None

def find_galaxytoolshed_link(link):
    '''
    Find Galaxy toolshed in URL string
    '''
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?toolshed\.galaxyproject\.org')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None



def prepare_sources_labels(tool):
    '''
    {
        "biotools" : URL,
        "bioconda" : URL,
        "biocontainers" : URL,
        "galaxy" : URL,
        "toolshed" : URL,
        "bioconductor" : URL,
        "sourceforge" : URL,
        "github" : URL,
        "bitbucket" : URL,
    }
    '''
    sources_labels = {}
    remain_sources = tool['source'].copy()

    if 'opeb_metrics' in remain_sources:
        remain_sources.remove('opeb_metrics')

    if 'biotools' in tool['source']:
        sources_labels['biotools'] = f'https://bio.tools/{tool["name"]}'
        remain_sources.remove('biotools')

    if 'bioconda' in tool['source'] or 'bioconda_recipes' in tool['source']:
        sources_labels['bioconda'] = f'https://anaconda.org/bioconda/{tool["name"]}'
        if 'bioconda_recipes' in tool['source']:
            remain_sources.remove('bioconda_recipes')
        if 'bioconda' in tool['source']:
            remain_sources.remove('bioconda')

    if 'bioconductor' in tool['source']:
        sources_labels['bioconductor'] = f'https://bioconductor.org/packages/release/bioc/html/{tool["name"]}.html'
        remain_sources.remove('bioconductor')
    
    if 'sourceforge' in tool['source']:
        sources_labels['sourceforge'] = f'https://sourceforge.net/projects/{tool["name"]}'
        remain_sources.remove('sourceforge')
    
    if 'toolshed' in tool['source']:
        sources_labels['toolshed'] = f'https://toolshed.g2.bx.psu.edu/repository'
        remain_sources.remove('toolshed')

    if 'galaxy_metadata' in remain_sources:
        sources_labels['toolshed'] = f'https://toolshed.g2.bx.psu.edu/repository'
        remain_sources.append('galaxy')
        remain_sources.remove('galaxy_metadata')
    
    if 'galaxy' in tool['source']:
        sources_labels['galaxy'] = 'https://usegalaxy.eu/'
        remain_sources.remove('galaxy')

    repos = tool.get('repository', None)
    for repo in repos:
        if repo.get('kind') == 'github':
            sources_labels['github'] = repo.get('url')
            remain_sources.remove('github')
        
        if repo.get('kind') == 'bioconductor':
            sources_labels['bioconductor'] = repo.get('url')
            remain_sources.remove('bioconductor')

        if repo.get('kind') == 'bitbucket':
            sources_labels['bitbucket'] = repo.get('url')
            remain_sources.remove('bitbucket')
        


    for link in tool['links']:
        foundLink = False
        while not foundLink:
            # bioconda
            # some tools have bioconductor in name in some sources like bioconda
            if f'bioconductor-{tool["name"]}' in link:
                sources_labels['bioconda'] = f'https://anaconda.org/bioconda/bioconductor-{tool["name"]}'
            
            # bioconductor
            bioconductor_link = find_bioconductor_link(link)
            if bioconductor_link:
                sources_labels['bioconductor'] = bioconductor_link
                foundLink = True
                if 'bioconductor' in remain_sources:
                    remain_sources.remove('bioconductor')
            
            # bitbucket 
            bitbucket_repo = find_bitbucket_repo(link)
            if bitbucket_repo:
                sources_labels['bitbucket'] = bitbucket_repo
                foundLink = True
                if 'bitbucket' in remain_sources:
                    remain_sources.remove('bitbucket')

            # galaxy
            galaxy_instance = find_galaxy_instance(link)
            if galaxy_instance:
                sources_labels['galaxy'] = galaxy_instance
                foundLink = True
                if 'galaxy' in remain_sources:
                    remain_sources.remove('galaxy')

            # toolshed
            galaxytoolshed_link = find_galaxytoolshed_link(link)
            if galaxytoolshed_link:
                sources_labels['toolshed'] = galaxytoolshed_link
                foundLink = True
                if 'toolshed' in remain_sources:
                    remain_sources.remove('toolshed')

            foundLink = True

    for source in remain_sources:
        sources_labels[source] = ''

    tool['sources_labels'] = sources_labels
    return(tool)


def get_version():
    # Get the absolute path to the VERSION file
    version_path = Path(__file__).parent.parent.parent / "VERSION"
    
    # Read the VERSION file
    return version_path.read_text().strip()
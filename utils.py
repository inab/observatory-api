import configparser
import re

from pymongo import MongoClient

from EDAM_forFE import EDAMDict


########
# Tool preparation functions
# These functions prepare the tool metadata to be displayed in the UI
#######

def prepareToolMetadata(tool):
    '''
    Triggers all the preparation functions sequentially
    '''
    tool.pop('_id')
    # Several fields need processing to be displayed in the UI:
    ## Prepare description
    tool = prepareDescription(tool)
    ## Prepare topics and operations
    tool = prepareTopicsOperations(tool, 'edam_topics', 'topics')
    tool = prepareTopicsOperations(tool, 'edam_operations', 'operations')
    ## Prepare documentation
    tool = prepareDocumentation(tool)
    ## Prepare authors 
    tool = prepareAuthors(tool)
    ## Prepare license
    tool = prepareLicense(tool)
    ## Prepare publications
    tool = preparePublications(tool)
    ## Prepare src
    tool = prepareSrc(tool)
    ## Prepare os
    tool = prepareOS(tool)
    ## Prepare input and output data formats
    tool = prepareDataFormats(tool, 'input')
    tool = prepareDataFormats(tool, 'output')
    # Extract webpages from links
    tool = getWebPage(tool)
    # Add ids to lists for v-for loops to work in the UI
    tool = prepareListsIds(tool)

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
        term = EDAMDict[item]
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
            "url": "http://edamontology.org/format_1929",
            datatype: {
                "vocabulary": "EDAM",
                "term": "Sequence",
                "url": "http://edamontology.org/data_0006"
            }
        },
        ...
    ]
    
    '''
    items = metadata[field]
    new_items = []
    # look up for each item in the list the corresponding label
    for item in items:
        datatype = {
            'vocabulary': 'EDAM',
            'term': EDAMDict[item['datatype']],
            'uri': item['datatype']
        }
        for format in item['formats']:
            format = {
                'vocabulary': 'EDAM',
                'term': EDAMDict[format],
                'uri': format,
                'datatype': datatype
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
        'src',
        'links',
        'topics',
        'operations',
        'input',
        'output',
        'repository',
        'dependencies',
        'os',
        'authors',
        'publication'
    ]

    for field in fields:
        new_list = [] 
        i=0
        for item in metadata[field]:
            new_item ={
                'term': item,
                'id': i
            }
            new_list.append(new_item)
            i+=1

        metadata[field] = new_list
    
    return metadata


def getWebPage(metadata):
    '''
    Returns the webpage of a tool
    '''
    webpages= []
    new_links= []
    for link in metadata['links']:
        x = re.search("^(.*)(\.)(rar|bz2|tar|gz|zip|bz|json|txt|js|py|md)$", link)
        if x:
            new_links.append(link)
        else:
            webpages.append(link)
    
    metadata['webpage'] = webpages
    metadata['links'] = new_links

    return metadata

def clean_brakets(string):
    '''
    Remove anything between {}, [], or <>, or after {, [, <
    '''
    def clena_after_braket(string):
        '''
        Remove anything between {}, [], or <>
        '''
        pattern = re.compile(r'\{.*|\[.*|\(.*|\<.*')
        return re.sub(pattern, '', string)

    def clean_between_brakets(string):
        '''
        Remove anything between {, [, <
        '''
        pattern = re.compile(r'\{.*?\}|\[.*?\]|\(.*?\)|\<.*?\>')
        return re.sub(pattern, '', string)


    string = clean_between_brakets(string)
    string = clena_after_braket(string)
    return string

def clean_doctor(string):
    '''
    remove title at the begining of the string
    '''
    pattern = re.compile(r'^Dr\.|Dr |Dr\. |Dr')
    return re.sub(pattern, '', string)

def keep_after_code(string):
    '''
    Remove anything before code and others
    '''
    if 'initial R code' in string:
        return ''
    if 'contact form' in string:
        return ''
    else:
        pattern = re.compile(r'.*?code')
        string = re.sub(pattern, '', string)
        pattern = re.compile(r'.*?Code')
        string = re.sub(pattern, '', string)
        pattern = re.compile(r'.*?from')
        string = re.sub(pattern, '', string)
        return re.sub(pattern, '', string)

def clean_first_end_parenthesis(string):
    if string[0] == '(' and string[-1] == ')':
        string = string[1:]
        string = string[:-1]

    return string

def clean_spaces(string):
    '''
    Clean spaces around the string
    '''
    return string.strip()


def classify_person_organization(string):
    '''
    tokenize the string
    if any of the words in the string is in the list of keywords
    then it is an institution
    otherwise it is a person
    '''
    inst_keywords = [
        'university',
        'université',
        'universidad',
        'universidade',
        'università',
        'universität',
        'institut',
        'institute',
        'college',
        'school',
        'department',
        'laboratory',
        'laboratoire',
        'lab',
        'center',
        'centre',
        'research',
        'researcher',
        'researchers',
        'group',
        'support',
        'foundation',
        'company',
        'corporation',
        'team',
        'helpdesk',
        'service',
        'platform',
        'program',
        'programme',
        'community'
    ]
    words = string.split()
    for word in words:
        if word.lower() in inst_keywords:
            return 'organization'
    return 'person'

def clean_long(string):
    if len(string.split()) >= 5:
        return ''
    else:
        return string


def build_organization(string):
    return {
        'type': 'organization',
        'first_name': string
        }

def build_person(string):
    '''
    Extract first and last name from a string
    '''
    if string:
        names = string.split()
        if len(names) == 1:
            return {
                'type': 'person' ,
                'first_name': names[0], 
                'last_name': '',
                'email': '',
                'maintainer': False
                }
        else:
            return {
                'type': 'person', 
                'first_name': names[0], 
                'last_name': names[-1],
                'email': '',
                'maintainer': False}


def build_authors(authors):
    '''
    Build a list of authors
    '''
    new_authors = []
    for author in authors:
        name = clean_first_end_parenthesis(author)
        name = clean_brakets(name)
        name = clean_doctor(name)
        name = keep_after_code(name)
        name = clean_spaces(name)
        classification = classify_person_organization(name)
        if classification == 'person':
            if name:
                name = clean_long(name)
                person = build_person(name)
                new_authors.append(person)

        else:
            organization = build_organization(name)
            new_authors.append(organization)

    return new_authors

def prepareAuthors(tool):
    '''
    {
        "name": "name1",
        "email": "email1",
        "type": "person/organization",
        "maintainer": "true/false"
    }
    '''
    authors = build_authors(tool['authors'])

    new_authors = []
    for author in authors:
        new_author = author
        new_authors.append(new_author)
    
    tool['authors'] = new_authors
    return tool
    


def prepareLicense(tool):
    '''
    {
        "name": "name1",
        "url": "url1"
    }
    '''
    licenses_set= set(tool['license'])
    tool['license'] = list(licenses_set)

    def remove_file_LICENSE(license):
        z = re.match("(.*)\s?\+\s?file\s?LICENSE", license)
        if z:
            license = z.groups(0)[0]
        return license
    
    new_licenses = []
    for license in tool['license']:
        new_license = {
            'name': remove_file_LICENSE(license),
            'url': ''
        }
        new_licenses.append(new_license)
    
    tool['license'] = new_licenses
    return tool

def prepareDescription(tool):
    description = set(tool['description'])
    tool['description'] = list(description)
    return tool

def preparePublications(tool):
    '''
    Merge publications that share ids or title
    '''
    identifiers = ['pmcid', 'pmid', 'doi', 'title']

    def indices(lst, item):
       return [i for i, x in enumerate(lst) if x == item]

    def merge_by_id(publications, id_):
        seen_ids = []
        ids= [pub.get(id_) for pub in publications]
        new_publications = []
        
        # get indexes of repeated pmcids
        for id in ids:
            if id != None:
                if id in seen_ids:
                    continue
                else:
                    seen_ids.append(id)
                    indexes = indices(ids, id)
                    new_publication = {}
                    # merge repeated publications by pairs
                    if len(indexes) > 1:
                        # merge needed
                        for i in indexes:
                            new_publication = new_publication | publications[i]
                        
                        # merged publications
                        new_publications.append(new_publication)
                    else:
                        # no possible merge. Append publication as it is
                        index = indexes[0]
                        new_publications.append(publications[index])
            else:
                # append publication of that id
                index = ids.index(id)
                new_publications.append(publications[index])

        return new_publications
    
    publications = tool['publication']
    for id_ in identifiers:
        publications = merge_by_id(publications, id_)
    
    tool['publication'] = publications
    
    return tool


def prepareSrc(tool):
    print(tool['src'])
    links=set(tool['src'])
    tool['src'] = list(links)
    return tool


def prepareOS(tool):
    new_os = []
    for os in tool['os']:
        if os == 'Mac':
            new_os.append('macOS')
        else:
            new_os.append(os)
    
    tool['os'] = new_os
    return tool


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
        'src',
        'links',
        'input',
        'output',
        'repository',
        'dependencies',
        'os',
        'authors',
        'publication',
        'topics', # added by prepareTopicsOperations
        'operations', # added by prepareTopicsOperations
        'webpage' # added by getWebPage
    ]

    for field in fields:
        new_list = [] 
        for item in metadata[field]:
            print(item)
            print(field)
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
    tool['label'] = tool['label'][0]
    
    return tool

################
# Database connection
################
def connect_DB():
    # connecting to db
    config = configparser.ConfigParser()
    config.read('config_db.ini')
    DBHOST = config['MONGO_DETAILS']['DBHOST']
    DBPORT = config['MONGO_DETAILS']['DBPORT']
    DATABASE = config['MONGO_DETAILS']['DATABASE']
    TOOLS = config['MONGO_DETAILS']['TOOLS']
    STATS = config['MONGO_DETAILS']['STATS']
    DISCOVERER = 'tools_discoverer_w_index'

    # hardcaded to test the new db configuration
    connection = MongoClient(DBHOST, int(DBPORT))
    tools_collection = connection['observatory2']['tools']
    discoverer_collection = connection['observatory2'][DISCOVERER] # used by endpoint "/tools/names_type_labels"
    stats = connection[DATABASE][STATS]

    return tools_collection, discoverer_collection, stats
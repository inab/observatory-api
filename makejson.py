from datetime import datetime
from EDAM_forFE import EDAMDict 

def get_description(descriptions):
    if descriptions:
        return descriptions[0]
    else:
        return ""

def remove_empty_values(d):
    """
    Remove empty values from a dictionary
    """
    return {k: v for k, v in d.items() if v}

def get_single_author(author):
    if author.get('type').lower() == 'person':
        new_author = {
        "@type": "https://schema.org/Person",
        "schema:name": author.get('name'),
        "schema:email": author.get('email')
    }
    else:  
        new_author = {
            "@type": "https://schema.org/Organization",
            "schema:name": author.get('first_name'),
            "schema:email": author.get('email')
        }

    return remove_empty_values(new_author)


def get_authors(authors):
    new_authors = []
    if authors:
        for author in authors:
            new_author = get_single_author(author)
            new_authors.append(remove_empty_values(new_author))
    
        return new_authors
    
    else:
        return ""
    

def get_license(licenses):
    new_licenses = []
    if licenses:
        for license in licenses:
            new_license = {
                "@type": "https://schema.org/CreativeWork",
                "schema:name": license.get('name'),
                "schema:url": license.get('url')
            }
            
            new_licenses.append(remove_empty_values(new_license))

        return new_licenses
    
    else:
        return ""
    
def get_keywords(topics):
    new_topics = []
    if topics:
        for topic in topics:
            if topic.get('vocabulary') == 'EDAM' and topic.get('uri').startswith('http://edamontology.org/'):
                identifier = f"edam:{topic['uri'].split('/')[-1]}"
                new_topics.append(identifier)

            else:
                if topic.get('uri'):
                    identifier = topic.get('uri')
                    new_topics.append(identifier)
                else:
                    new_topics.append(identifier)
            
        return new_topics
    
    else:
        return ""
    


def get_citation(citations):
    new_citations = []
    if citations:
        for citation in citations:
            new_citation = []
            if citation.get('pmcid'):
                new_citation.append(f"pmcid:{citation.get('pmcid')}")
            if citation.get('pmid'):
                new_citation.append(f"pmid:{citation.get('pmid')}")
            if citation.get('doi'):
                new_citation.append({
                    "@id": citation.get('doi'),
                })
            if citation.get('title') and citation.get('authors') and citation.get('journal'):
                new_citation.append({
                    "@type": "https://schema.org/CreativeWork",
                    "@id": f"doi:{citation.get('doi')}",
                    "schema:name": citation.get('title'),
                    "schema:author": get_single_author(citation.get('authors')),
                    "schema:isPartOf": citation.get('journal')
                })
            
                new_citations.append(remove_empty_values(new_citation))

        return new_citations
    
    else:
        return ""
    
    
def get_input(inputs):
    if inputs:
        items = []
        for input in inputs:
            if input.get('uri'):
                new_input = {
                    "@type": "https://bioschemas.org/FormatParameter",
                    "biochemas:encodingFormat": f"edam:{input.get('uri').split('/')[-1]}"
                }
            else:
                new_input = {
                    "@type": "https://bioschemas.org/FormatParameter",
                    "bioschemas:encodingFormat": input.get('term')
                }

            items.append(remove_empty_values(new_input))

        return items
    
    else:
        return ""
    
    

def get_readme(documentations):
    if documentations:
        for documentation in documentations:
            if documentation.get('type') == 'readme':
                return documentation.get('url')
    else:
        return ""


def get_help(documentations):
    new_documentation = []
    if documentations:
        for documentation in documentations:
            if documentation.get('url'):
                new_doc = {
                    "@id": documentation.get('url'),
                }
                new_documentation.append(remove_empty_values(new_doc))
    else:
        return ""
    
    return new_documentation


def get_maintainer(authors):
    maintainers = []
    if authors:
        for author in authors:
            if author.get('maintainer') == True:
                if author.get('type').lower() == 'person':
                    new_maintainer = {
                    "@type": "https://schema.org/Person",
                    "schema:name": author.get('name'),
                    "schema:email": author.get('email')
                }
                else:  
                    new_maintainer = {
                        "@type": "https://schema.org/Organization",
                        "schema:name": author.get('name'),
                        "schema:email": author.get('email')
                    }
                maintainers.append(remove_empty_values(new_maintainer))
        return maintainers
    else:
        return ""

def get_webpage(webpages):
    if webpages:
        return webpages
    else:
        return ""
    
def get_type(type):
    value = f'htpps://openebench.bsc.es/bioschemas/oebtools#{type}'
    return value

def get_identifier(meta):
    value = f"https://openebench.bsc.es/bioschemas/tools/observatory:{meta.get('name')}:{meta.get('version')}/{meta.get('type')}"
    return value


def build_date():
    # current date and time
    now = datetime.now()

    t = now.strftime("%H:%M:%S")
    print("Time:", t)

    s1 = now.strftime("%m/%d/%YT%H:%M:%SZ")

    return s1

def build_json_ld(meta):
    """
    Build JSON-LD from tool metadata
    """
    context =  {
        "@import" : "https://openebench.bsc.es/bioschemas/oebtools.jsonld"
    }
    metadata = {
        "@context": context,
        "@type": get_type(meta.get('type')),
        "schema:applicationSubcategory": get_keywords(meta.get('topics')),
        "schema:additionalType": meta.get('type'),
        "schema:name": meta.get('name'),
        "@id": get_identifier(meta),
        "schema:url": get_webpage(meta.get('webpages')),
        "schema:description": get_description(meta.get('description')),
        "schema:applicationCategory": meta.get('type'),
        "schema:operatingSystem": meta.get('os'),
        "schema:license":get_license(meta.get('license')),
        "schema:author": get_authors(meta.get('authors')),
        "schema:maintainer": get_maintainer(meta.get('authors')),
        "schema:softwareVersion" : meta.get('version'),
        "schema:codeRepository": meta.get('repository'),
        "schema:featureList": get_keywords(meta.get('operations')),
        "bioschemas:input": get_input(meta.get('input')),
        "bioschemas:output": get_input(meta.get('output')),
        "schema:downloadURL": meta.get('download'),
        "schema:softwareHelp": get_help(meta.get('documentation')),
        "schema:citation": get_citation(meta.get('publication')),
        "schema:requirements": meta.get('dependencies'),
        "schema:isAccessibleForFree": meta.get('registration_not_manadatory'),
        "schema:dateModified": build_date(),
        
    }


    metadata = remove_empty_values(metadata)

    return metadata



def build_fe_topics_operations(topics):
    if topics:
        items = []
        for topic in topics:
            label = topic.get('term').split(':')[-1]
            uri = f'https://edamontology.org/{label}'
            new_topic = {
                "term": EDAMDict.get(uri),
                "uri": uri,
                "vocabulary":'EDAM'
            }
            items.append(remove_empty_values(new_topic))
        return items
    else:
        return ""
    

def build_fe_description(description):
    if description:
        return [description]
    else:
        return ""


def build_fe_license(licenses):
    '''
    [{   
        "@type": "https://schema.org/CreativeWork",
        "schema:name": "MIT License",
    },
    ...
    ]
    '''
    new_licenses = []
    if licenses:
        for license in licenses:
            new_licenses.append(license['schema:name'])
        return new_licenses
    else:
        return ""
    
def build_fe_authors(authors):
    '''
    [
        {
            "@type": "https://schema.org/Person",
            "schema:name": "John Doe",
            "schema:email": "email@gmail.com"
        },
        ...
    ]
    '''
    new_authors = []
    if authors:
        for author in authors:
            new_author = {
                "type": author['@type'].split('/')[-1].lower(),
                "name": author['schema:name'],
                "email": author['schema:email'],
                "maintainer": False 
            }
            new_authors.append(remove_empty_values(new_author))
        
        return new_authors
    
    else:
        return ""

def build_fe_version(version):
    if version:
        return [version]
    else:
        return ""
    

def build_fe_input_output(input_output):
    if input_output:
        items = []
        for io in input_output:
            label = io.get('term').split(':')[-1]
            uri = f'https://edamontology.org/{label}'
            new_io = {
                "datatype": {
                    "term":"",
                    "uri":"",
                    "vocabulary":""
                },
                "term": EDAMDict.get(uri),
                "uri": uri,
                "vocabulary":"EDAM"
            }
            items.append(remove_empty_values(new_io))
        return items
    else:
        return ""



def build_frontend_metadata(meta):
    '''
    Build frontend metadata from bioschema metadata
    '''
    metadata = {
        "type": meta.get('@type'),
        "topics": build_fe_topics_operations(meta.get('schema:applicationSubcategory')),
        "name": meta.get('schema:name'),
        "webpages": meta.get('schema:url'),
        "description": build_fe_description(meta.get('schema:description')),
        "os": meta.get('schema:operatingSystem'),
        "license": build_fe_license(meta.get('schema:license')),
        "authors": build_fe_authors(meta.get('schema:author')),
        "version": build_fe_version(meta.get('schema:softwareVersion')),
        "repository": meta.get('schema:codeRepository'),
        "operations":build_fe_topics_operations(meta.get('schema:featureList')),
        "input":build_fe_input_output(meta.get('bioschemas:input')),
        "output":build_fe_input_output(meta.get('bioschemas:output')),
        "download":'',
        "documentation":'',
        "publication":'',
        "dependencies":'',
        "registration_not_manadatory":''
    }

    return
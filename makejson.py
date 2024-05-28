'''
TODO: Fix the following: 

1. DONE Fixed the typo in bioschemas:encodingFormat.
2. DONE Changed the incorrect property types and URLs to correct ones (schema:Person, schema:CreativeWork).
3. DONE Fixed the schema:dateModified format to the correct ISO 8601 format.


TODO: Add the following:
- codemeta:buildInstructions
- codemeta:readme
- codemeta:referencePublication
- maSMP:changelog
- maSMP:deployInstructions
- maSMP:developerInstructions
- maSMP:userDocumentation
- maSMP:versionControlSystem

TODO: Remove shema:citation
'''



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
        "@type": "schema:Person",
        "schema:name": author.get('name'),
        "schema:email": author.get('email')
    }
    else:  
        new_author = {
            "@type": "schema:Organization",
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
                "@type": "schema:CreativeWork",
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
    '''
    Add journal information to the citation. Not in Fronttend
    '''
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
                    "@id": f"doi:{citation.get('doi')}",
                })

            if citation.get('title'):
                new_citation.append({
                    "@type": "schema:CreativeWork",
                    "@id": f"doi:{citation.get('doi')}",
                    "schema:name": citation.get('title'),
                    #"schema:isPartOf": citation.get('journal')
                })
            
            new_citations.append(new_citation)

        return new_citations
    
    else:
        return ""


def get_reference_publication(citations):
    """
    Build a list of reference publications
    """
    refPubs = []    
    for citation in citations:
        print(citation)
        name = citation.get('title')
        if citation.get('doi'):
            url = f"https://doi.org/{citation.get('doi')}"
        else:
            url = ""
        
        if name or url:
            publication = {
                "@type": "schema:CreativeWork",
                "@id": url,
                "schema:name": name,
                "schema:url": url
            }
            refPubs.append(remove_empty_values(publication))

    return refPubs

def get_userDocumentation(documentations):
    """
    Build a list of user documentation
    """
    userDocs = []
    for documentation in documentations:
        if documentation.get('type') == 'user' or documentation.get('type') == 'general':
            name = documentation.get('title')
            url = documentation.get('url')
            if name or url:
                doc = {
                    "@type": "schema:CreativeWork",
                    "@id": url,
                    "schema:name": name,
                    "schema:url": url
                }
                userDocs.append(remove_empty_values(doc))

    return userDocs




    
def get_input(inputs):
    if inputs:
        items = []
        for input in inputs:
            if input.get('uri'):
                new_input = {
                    "@type": "https://bioschemas.org/FormatParameter",
                    "bioschemas:encodingFormat": f"edam:{input.get('uri').split('/')[-1]}"
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
                    "@type": "schema:Person",
                    "schema:name": author.get('name'),
                    "schema:email": author.get('email')
                }
                else:  
                    new_maintainer = {
                        "@type": "schema:Organization",
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

    s1 = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    return s1

def build_json_ld(meta):
    """
    Build JSON-LD from tool metadata
    """
    print(meta)
    context =  {
        "schema": "http://schema.org/",
        "bs": "https://bioschemas.org/terms/",
        "codemeta": "https://w3id.org/codemeta/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "maSMP": "https://discovery.biothings.io/view/maSMP/"
        }
    metadata = {
        "@context": context,
        "@type": "schema:SoftwareApplication",
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
        "schema:requirements": meta.get('dependencies'),
        "schema:isAccessibleForFree": meta.get('registration_not_manadatory'),
        "schema:dateModified": build_date(),
        "codemeta:referencePublication": get_reference_publication(meta.get('publication')),
        "codemeta:readme": get_readme(meta.get('documentation')),
        "maSMP:userDocumentation": get_userDocumentation(meta.get('documentation')),
        
    }

    metadata = remove_empty_values(metadata)

    return metadata




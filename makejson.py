

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
    new_author = {
        "@type": "Person",
        "givenName": author.get('name'),
        "familyName": author.get('surname'),
        "email": author.get('email')
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
                "@type": "CreativeWork",
                "name": license.get('name'),
                "url": license.get('url')
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
                new_topic = {
                    "@id": identifier,
                }
                new_topics.append(remove_empty_values(new_topic))
            else:
                if topic.get('uri'):
                    identifier = topics.get('uri')
                    new_topic = {
                        "@id": identifier,
                    }
                    new_topics.append(remove_empty_values(new_topic))
                else:
                    new_topic = {
                        "@id": topic.get('term'),
                    }
                    new_topics.append(remove_empty_values(new_topic))
            
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
                    "@type": "CreativeWork",
                    "@id": f"doi:{citation.get('doi')}",
                    "name": citation.get('title'),
                    "author": get_single_author(citation.get('authors')),
                    "isPartOf": citation.get('journal')
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
                    "@type": "FormatParameter",
                    "encodingFormat": {
                        "@id": f"edam:{input.get('uri').split('/')[-1]}"
                    }
                }
            else:
                new_input = {
                    "@type": "FormatParameter",
                    "encodingFormat": input.get('term')
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
                new_maintainer = {
                    "@type": "Person",
                    "givenName": author.get('name'),
                    "familyName": author.get('surname'),
                    "email": author.get('email')
                }
                maintainers.append(remove_empty_values(new_maintainer))
        return maintainers
    else:
        return ""

def get_webpage(webpages):
    if webpages:
        return webpages[0]
    else:
        return ""

def build_json_ld(meta):
    """
    Build JSON-LD from tool metadata
    """
    context = "http://schema.org/" # chance for OEB
    metadata = {
        "@context": context,
        "@type": "SoftwareApplication",
        "additionalType": meta.get('type'),
        "name": meta.get('name'),
        "description": get_description(meta.get('descriptions')),
        "author": get_authors(meta.get('authors')),
        "license": get_license(meta.get('license')),
        "url": get_webpage(meta.get('webpages')),
        "version" : meta.get('version'),
        "codeRepository": meta.get('repository'),
        "applicationSubcategory": get_keywords(meta.get('topics')),
        "featureList": get_keywords(meta.get('operations')),
        "downloadURL": meta.get('download'),
        "operatingSystem": meta.get('os'),
        "citation": get_citation(meta.get('publication')),
        "softwareRequirements": meta.get('dependencies'),
        "isAccessibleForFree": meta.get('registration_not_manadatory'),
        "input": get_input(meta.get('input')),
        "output": get_input(meta.get('output')),
        "readme": get_readme(meta.get('documentation')),
        "softwareHelp": get_help(meta.get('documentation')),
        "maintainer": get_maintainer(meta.get('authors')),
    }

    metadata = remove_empty_values(metadata)

    return metadata
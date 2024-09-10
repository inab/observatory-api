import yaml
from cffconvert import Citation

def validate_cff_dict(cff_string: dict) -> bool:
    try:
        # Load the CFF content from the YAML string
        citation = Citation.from_string(cff_string)
        
        # Perform validation
        citation.validate()
        
        # If no exception is raised, the validation is successful
        return True
    except Exception as e:
        # If there is an exception, print the error and return False
        print(f"Validation failed: {e}")
        return False



def create_cff(metadata):
    cff_data = {
        'cff-version': '1.2.0',
        'message': 'If you use this software, please cite it as below.'
    }
    if metadata.get('name'):
        cff_data['title'] = metadata.get('name')
    
    if metadata.get('version'):
        cff_data['version'] = metadata.get('version')
    
    if metadata.get('license'):
        license_name = metadata.get('license')[0].get('name')
        license_url = metadata.get('license')[0].get('url')
        if license_name:
            cff_data['license'] = license_name
        elif license_url:
            cff_data['license'] = license_url

    if metadata.get('tags'):
        cff_data['keywords'] = metadata.get('tags')
    
    if metadata.get('repository'):
        cff_data['repository'] = metadata['repository'][0]
    
    if metadata.get('webpage'):
        cff_data['url'] = metadata['webpage'][0]    

    if metadata.get('authors'):
        cff_data['authors'] = []

        for author in metadata['authors']:
            cff_data['authors'].append({
                'name': author['name'],
                'email': author['email'] if author['email'] else None,
            })

    if metadata.get('publication'):
        cff_data['references'] = []

        for publication in metadata['publication']:
            entry = {}
            if publication.get('doi'):
                entry['doi'] = publication['doi']
            if publication.get('title'):
                entry['title'] = publication['title']
            if publication.get('year'):
                entry['year'] = publication['year']
            if publication.get('journal'):
                entry['journal'] = publication['journal']
            cff_data['references'].append(entry)


    cff_string = yaml.dump(cff_data, sort_keys=False)

    if validate_cff_dict(cff_string):
        return cff_string
    else:        
        return None


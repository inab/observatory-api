import yaml

def create_cff(metadata):
    cff_data = {
        'cff-version': '1.2.0',
        'message': 'If you use this software, please cite it as below.',
        'title': metadata['name'],
        'version': metadata['version'],
        'authors': [],
        'keywords': metadata['tags'],
        'license': metadata['license'][0]['name'] if metadata['license'] else None,
        'repository-code': metadata['repository'][0] if metadata['repository'] else None,
        'url': metadata['webpage'][0] if metadata['webpage'] else None,
        'references': [],
    }

    for author in metadata['authors']:
        cff_data['authors'].append({
            'name': author['name'],
            'email': author['email'] if author['email'] else None,
        })

    for publication in metadata['publication']:
        cff_data['references'].append({
            'type': 'article',
            'title': publication['title'],
            'doi': publication['doi'],
            'year': publication['year'],
            'journal': publication['title']
        })

    cff_yaml = yaml.dump(cff_data, sort_keys=False)
    return cff_yaml
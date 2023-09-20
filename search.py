from utils import prepareToolMetadata
from utils import connect_DB

tools_collection, stats = connect_DB()

def search_input(tools, counts, search, label):
    for tool in tools_collection.find(search):
        # skip tools that are only in galaxy_metadata
        if tool['source'] == ['galaxy_metadata']:
            continue
        else:
            entry = prepareToolMetadata(tool)
            if entry['@id'] in tools.keys():
                tools[entry['@id']]['foundIn'].append(label)
            else:
                entry['foundIn'] = [label]
                tools[entry['@id']] = entry

            counts[label] += 1

    return tools, counts

def make_search(label, query_field, query_expression, search, tools, counts):
    search = search.copy()
    search[query_field] = query_expression

    search = {'$and': [{key:value} for key, value in search.items()  ] }
    tools, counts = search_input(tools, counts, search, label)
    return tools, counts

def calculate_stats(tools):
    stats = {
        'type': {},
        'source': {},
        'topics': {},
        'operations': {},
        'license': {},
        'input': {},
        'output': {},
        'collection': {}
    }
    for tool in tools:
        #---- TYPE --------
        if tool['type'] in stats['type'].keys():
            stats['type'][tool['type']] += 1
        else:
            stats['type'][tool['type']] = 1
        
        #---- SOURCE --------
        seen_sources = []
        for source in tool['source']:
        
            if source == 'opeb_metrics':
                continue
            
            # bioconda_recipes and bioconda are the same for this purpose
            if source == 'bioconda_recipes':
                if 'bioconda' in seen_sources:
                    continue
                else:
                    source = 'bioconda'

            # galaxy_metadata and toolshed are the same for this purpose
            if source == 'galaxy_metadata':
                if 'toolshed' in seen_sources:
                    continue
                else:
                    source = 'toolshed'

            if source in stats['source'].keys():
                seen_sources.append(source)
                stats['source'][source] += 1
            else:
                seen_sources.append(source)
                stats['source'][source] = 1 

        #---- TOPICS ------------
        for edam_topic in tool['edam_topics']:
            if edam_topic in stats['topics'].keys():
                stats['topics'][edam_topic] += 1
            else:
                stats['topics'][edam_topic] = 1 

        #---- OPERATIONS --------
        for edam_operation in tool['edam_operations']:
            if edam_operation in stats['operations'].keys():
                stats['operations'][edam_operation] += 1
            else:
                stats['operations'][edam_operation] = 1

        #---- LICENSE -----------
        for license in tool['license']:
            license = license['name']
            if license in stats['license'].keys():
                stats['license'][license] += 1
            else:
                stats['license'][license] = 1      

        #---- INPUT -------------
        # Data format (FASTA, CSV, ...)
        # Not data type for now
        for item in tool['input']:
            if item['uri']:
                term = item['uri']
            else:
                term = item['term']

            if term in stats['input'].keys():
                stats['input'][term] += 1
            else:
                stats['input'][term] = 1

        #---- OUTPUT ------------
        for item in tool['output']:
            if item['uri']:
                term = item['uri']
            else:
                term = item['term']

            if term in stats['output'].keys():
                stats['output'][term] += 1
            else:
                stats['output'][term] = 1

        #---- COLLECTION ----------
        for tag in tool['tags']:
            if tag in stats['collection'].keys():
                stats['collection'][tag] += 1
            else:
                stats['collection'][tag] = 1

    return stats
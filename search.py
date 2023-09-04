from utils import prepareToolMetadata
from utils import connect_DB

tools_collection, stats = connect_DB()

def search_input(tools, counts, search, label):
    for tool in tools_collection.find(search):
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
    tools, counts = search_input(tools, counts, search, label)
    return tools, counts

def calculate_stats(tools):
    stats = {
        'type': {},
        'source': {}
    }
    for tool in tools:
        # type
        if tool['type'] in stats['type'].keys():
            stats['type'][tool['type']] += 1
        else:
            stats['type'][tool['type']] = 1
        
        # source
        seen_sources = []
        for source in tool['source']:
        
            if source == 'opeb_metrics':
                continue

            if source == 'bioconda_recipes':
                if 'bioconda' in seen_sources:
                    continue
                else:
                    source = 'bioconda'

            if source in stats['source'].keys():
                seen_sources.append(source)
                stats['source'][source] += 1
            else:
                seen_sources.append(source)
                stats['source'][source] = 1 

    return stats
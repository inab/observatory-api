from app.helpers.database import connect_DB

tools_collection, stats, pubs_collection, availability_collection = connect_DB()

_total_stats_cache = None


def calculate_total_stats():
    global _total_stats_cache
    if _total_stats_cache is not None:
        return _total_stats_cache
    tools = [doc['data'] for doc in tools_collection.find(
        {}, projection={'data.type':1,'data.source':1,'data.topics':1,
                        'data.operations':1,'data.license':1,
                        'data.input':1,'data.output':1,'data.tags':1}
    )]
    _total_stats_cache = calculate_stats(tools)
    return _total_stats_cache

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
        for type in tool['type']:
            if type in stats['type'].keys():
                stats['type'][type] += 1
            else:
                stats['type'][type] = 1
        
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
        for edam_topic in tool['topics']:
            edam_topic = edam_topic['term'].strip('"')
            if edam_topic in stats['topics'].keys():
                stats['topics'][edam_topic] += 1
            else:
                stats['topics'][edam_topic] = 1

        #---- OPERATIONS --------
        for edam_operation in tool['operations']:
            edam_operation = edam_operation['term'].strip('"')
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
            term = item['uri'] or item['term']
            if not term:
                continue
            if term in stats['input'].keys():
                stats['input'][term] += 1
            else:
                stats['input'][term] = 1

        #---- OUTPUT ------------
        for item in tool['output']:
            term = item['uri'] or item['term']
            if not term:
                continue
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
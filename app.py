
import pymongo
import re
import configparser
import json

from pymongo import MongoClient
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS,cross_origin
from FAIRsoft.indicators_evaluation.FAIR_indicators_eval import computeScores_from_list
from EDAM_forFE import EDAMDict

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
        
## Init app
app = Flask(__name__)

## CORS
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})


def process_request(action, parameters):
    try:
        data = action(parameters)
        
    except Exception as err:
        print(f'Error here {err}')
        resp = make_response(err, 400)
        print(err)
    else:
        data = data
        resp = make_response(jsonify(data), 201)
    finally:
        return resp


def query(func):
    '''
    Error handling of query execution and removal of _id field
    '''
    def wrapper(*args, **kwargs):
        try:
            docs = func(*args, **kwargs)
        except Exception as err:
            raise
            return(str(err))
        else:
            [entry.pop('_id') for entry in docs]
        
        if len(docs) == 0:
            return('No results found')
        elif len(docs) == 1:
            return(docs[0])
        else:
            return(docs)
        
    return wrapper


def clean_quotations(string):
    string = string.replace('"', '')
    string = string.replace("'", '')
    return string

def prep_parameters(parameters):
    '''
    If version not stated, assign `latest` version
    If collection not stated, assign `tools` collection
    '''
    try:
        if parameters.get('version'):
            version = clean_quotations(parameters.get('version'))
        else:
            version = 'latest'
        
        if parameters.get('collection'):
            collection = clean_quotations(parameters.get('collection'))
        else:
            collection = 'tools'
        
    except Exception as err:
        return(('An error occurred while trying to read query parameters.'
            ' Please, check version and collection in your query and retry.'
            f' Error message: {str(err)}'))

    else:
        return collection, version
    
@query
def make_query(variable_name, parameters):
    collection, version = prep_parameters(parameters)
    if version == 'latest':
        record = list(stats.find({
            "variable":variable_name,
            "collection":collection,
            }).sort("version",-1).limit(1))
    else:
        record = list(stats.find({
            "variable":variable_name,
            "collection":collection,
            "version":version
            }))
    
    return record


## ROUTES ##

#####
## Requests regarding docs in `stats` collection
####

####### Trends 

# licenses-sunburst - licenses_summary_sunburst
@app.route('/stats/tools/licenses_summary_sunburst')
@cross_origin(origin='*',headers=['Content-Type'])
def licenses_summary_sunburst():
    resp = make_query('licenses_summary_sunburst', request.args)
    return(resp)

# licenses-bar - licenses_open_source
@app.route('/stats/tools/licenses_open_source')
@cross_origin(origin='*',headers=['Content-Type'])
def licenses_open_source():
    resp = make_query('licenses_open_source', request.args)
    return(resp)

# semantic versioning - semantic_versioning
@app.route('/stats/tools/semantic_versioning')
@cross_origin(origin='*',headers=['Content-Type'])
def semantic_versioning():
    resp = make_query('semantic_versioning', request.args)
    return(resp)


# version control yes/no counts - version_control_count
@app.route('/stats/tools/version_control_count')
@cross_origin(origin='*',headers=['Content-Type'])
def version_control_count():
    resp = make_query('version_control_count', request.args)
    return(resp)

# version control repositories counts - version_control_repositories
@app.route('/stats/tools/version_control_repositories')
@cross_origin(origin='*',headers=['Content-Type'])
def version_control_repositories():
    resp = make_query('version_control_repositories', request.args)
    return(resp)

# publications percentage in top most frequent journals and IF - publications_journals_IF
@app.route('/stats/tools/publications_journals_IF')
@cross_origin(origin='*',headers=['Content-Type'])
def publications_journals_IF():
    resp = make_query('publications_journals_IF', request.args)
    return(resp)

#### Data 

# Number of Tools per source
@app.route('/stats/tools/count_per_source')
@cross_origin(origin='*',headers=['Content-Type'])
def counts_per_source():
    resp =  make_query('tools_counts_per_source', request.args)
    #resp = process_request(counts_source_query, request.args)
    return(resp)

# Total Number of tools
@app.route('/stats/tools/count_total')
@cross_origin(origin='*',headers=['Content-Type'])
def count_total():
    resp = make_query('tools_count', request.args)
    return(resp)

# features 
@app.route('/stats/tools/features')
@cross_origin(origin='*',headers=['Content-Type'])
def features():
    resp = make_query('features', request.args)
    return(resp)

# coverage of sources
@app.route('/stats/tools/coverage_sources')
@cross_origin(origin='*',headers=['Content-Type'])
def coverage_sources():
    resp = make_query('coverage_sources', request.args)
    return(resp)   

# features cummulative - features_cummulative
@app.route('/stats/tools/features_cummulative')
@cross_origin(origin='*',headers=['Content-Type'])
def features_cummulative():
    resp = make_query('features_cummulative', request.args)
    return(resp)

# features xy - distribution_features
@app.route('/stats/tools/distribution_features')
@cross_origin(origin='*',headers=['Content-Type'])
def distribution_features():
    resp = make_query('distribution_features', request.args)
    return(resp)

# types tools - types_count
@app.route('/stats/tools/types_count')
@cross_origin(origin='*',headers=['Content-Type'])
def types_count():
    resp = make_query('types_count', request.args)
    return(resp)

#### FAIRness

# FAIR scores summary
@app.route('/stats/tools/fair_scores_summary')
@cross_origin(origin='*',headers=['Content-Type'])
def fair_scores_summary():
    resp = make_query('FAIR_scores_summary', request.args)
    return(resp)

# FAIR scores means 
@app.route('/stats/tools/fair_scores_means')
@cross_origin(origin='*',headers=['Content-Type'])
def fair_scores_means():
    resp = make_query('FAIR_scores_means', request.args)
    return(resp)

##################################
## Utils
##################################
def process_tool(tool):
    '''
    Processes a tool to return a dictionary with name, type and sources
    '''
    tool['label'] = tool['label'][0]
    
    return tool

# Retuns a list of tools with name, type and sources
@app.route('/tools/names_type_labels')
@cross_origin(origin='*',headers=['Content-Type'])
def names_type_labels():
    tools = list(discoverer_collection.find({},{'_id':0, '@id':1, 'label':1,'type':1,'sources_labels':1, 'name':1}))
    resp = []
    for tool in tools:
        resp.append(process_tool(tool))    
    return(resp)


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
    items = metadata['documentation']
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

def prepareAuthors(tool):
    '''
    {
        "name": "name1",
        "email": "email1"
        "mantainer: true/false"
    }
    '''
    new_authors = []
    for author in tool['authors']:
        new_author = {
            'name': author,
            'email': '',
            'maintainer': False
        }
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



@app.route('/EDAMTerms')
@cross_origin(origin='*',headers=['Content-Type'])
def EDAMTerms():
    try:
        from prepareVocabularies import prepareEDAM
        EDAMVocabularyItems = prepareEDAM()
    except:
        data = {'Something went wrong when retrieving the EDAM vocabulary :('}
        resp = make_response(data, 400)

    else:
        resp = make_response(jsonify(EDAMVocabularyItems), 200)

    return resp


@app.route('/SPDXLicenses')
@cross_origin(origin='*',headers=['Content-Type'])
def SPDXLicenses():
    # from file licenses.json
    try:
        with open('licenses.json') as f:
            data = json.load(f)
        
        SPDXLicenses = []
        for license in data['licenses']:
            SPDXLicenses.append(license['name'])
    except:
        data = {'Something went wrong when retrieving the SPDX licenses :('}
        resp = make_response(data, 400)
    else:
        resp = make_response(jsonify(SPDXLicenses), 200)

    return resp

@app.route('/SPDXLicenses/url/<license>')
@cross_origin(origin='*',headers=['Content-Type'])
def SPDXLicenseURL(license):
    # from file licenses.json
    try:
        with open('licenses.json') as f:
            data = json.load(f)
        URL=''
        for l in data['licenses']:
            if l['name'] == license:
                URL = l['reference']
                break
    except:
        data = {'Something went wrong when retrieving the URL of the SPDX license :('}
        resp = make_response(data, 400)
    else:
        data = {'URL': URL}
        resp = make_response(jsonify(data), 200)

    return resp

@app.route('/SPDXLicenses/match/<license>')
@cross_origin(origin='*',headers=['Content-Type'])
def SPDXLicenseMatch(license):
    # from file licenses.json
    try:
        with open('licenses.json') as f:
            data = json.load(f)
        match=''
        for l in data['licenses']:
            if l['name'] == license:
                match = l['licenseId']
                break
    except:
        data = {'Something went wrong when retrieving the SPDX license :('}
        resp = make_response(data, 400)
    else:
        data = {'match': match}
        resp = make_response(jsonify(data), 200)

    return resp

        
# returns a tool given its id
# Used by the FAIR evaluator to retrieve metadata of a tool
@app.route('/tools')
@cross_origin(origin='*',headers=['Content-Type'])
def tool_metadata():
    name = request.args.get('name')
    type_ = request.args.get('type')
    tool = tools_collection.find({'name': name, 'type': type_})
    tool = tool[0]
    
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

    resp = make_response(jsonify(tool), 200)
     
    return(resp)


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



# Evaluate FAIRness of a tool given its metadata
@app.route('/tools/evaluate', methods=['POST', 'GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def evaluate():
    '''
    Metadata is sent in the body of the request, inside a json object, 
    in the `tool_metadata` field.
    {
        "tool_metadata": {
            "name": "tool name",
            ...
        }       
    }
    '''
    data = request.get_json()
    if data:
        # Pre-process metadata
        tool = prepareMetadataForEvaluation(data['tool_metadata'])
        # Evaluate metadata
        scores = computeScores_from_list([tool])
        # Return scores
        resp = make_response(jsonify(scores), 200)

    else:
        data = {'message': 'No metadata provided', 'code': 'ERROR'}
        resp = make_response(data, 400)
        return(resp)
     
    return(resp)

# Evaluate FAIRness of a tool given its id
@app.route('/tools/evaluateId', methods=['POST', 'GET'])
@cross_origin(origins='*')
def evaluateId():
    if request.method == 'POST':
        data = request.get_json()
        id_ = data.get('id')
        # Get tool metadata
        if data:
            tool = tools_collection.find({'@id':id_})
            # Evaluate metadata
            scores = computeScores_from_list(list(tool))
            # Return scores
            resp = make_response(jsonify(scores), 200)
        else:
            data = {'message': 'No tool id or metadata provided', 'code': 'ERROR'}
            resp = make_response(data, 400)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return(resp)

     
        return(resp)


# Tools name, type and sources
#####
## Requests regarding docs in `tools_collection` collection
####

# Retrieve all tools
@app.route('/alltools', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def tools():
    try:
        tools = []
        [tools.append(entry) for entry in tools_collection.find({})]
        [entry.pop('_id') for entry in tools]
        data = {
            'tools' : tools
        }
    except Exception as err:
        data = {'message': f'Something went wrong while fetching tool entries: {err}', 'code': 'ERROR'}
        resp = make_response(data, 400)
        print(err)
    else:
        data = {'message': data, 'code': 'SUCCESS'}
        resp = make_response(jsonify(data), 201)
    finally:
        return resp




# Retrieve description of a tool by its name
# name as parameter
@app.route('/tool/description', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def description():
    try:
        tool_name = request.args.get('name')
        entry = tools_collection.find_one({'name' : tool_name})
        data = { 
            'name' : tool_name,
            'type': entry['type'],
            'description' : entry['description'][0]}
    except Exception as err:
        resp = make_response(err, 400)
        print(err)
    else:
        resp = make_response(jsonify(data), 201)
    finally:
        return resp



# Start the app
if __name__ == '__main__':
    app.run(debug=True, port=3000)





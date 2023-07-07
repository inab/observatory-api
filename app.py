
import json
import requests 

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS,cross_origin

from utils import prepareToolMetadata, prepareMetadataForEvaluation, prepareListsIds, keep_first_label, connect_DB
from prepareVocabularies import prepareEDAM
from FAIR_indicators_eval import computeScores_from_list
from makejson import build_json_ld

        
## Init app
app = Flask(__name__)

## CORS
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

## Connect to DB

tools_collection, stats = connect_DB()


##### helper function for routes #####

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
            }).sort("_id",-1).limit(1))
    else:
        record = list(stats.find({
            "variable":variable_name,
            "collection":collection,
            "version":version
            }))
    
    return record


## -------------------- ##
##       ROUTES         ##
## -------------------- ##

##-------------------------------------------------- ##
## Requests regarding docs in `stats` collection
##-------------------------------------------------- ##

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

##-------------------------------------------------- ##
##  Metadata
##-------------------------------------------------- ##

# retuns a list of tools with name, type and sources
@app.route('/tools/names_type_labels')
@cross_origin(origin='*',headers=['Content-Type'])
def names_type_labels():
    tools = list(tools_collection.find({ 
            'source' : { '$ne' : ['galaxy_metadata'] } # remove tools only in galaxy_metadata
        },
        {
            '_id':0, 
            '@id':1, 
            'label':1,
            'type':1,
            'sources_labels':1, 
            'name':1
        }
        ))
    resp = []
    for tool in tools:
        resp.append(keep_first_label(tool))    
    return(resp)
        
# returns a tool given its id
# Used by the FAIR evaluator to retrieve metadata of a tool
@app.route('/tools')
@cross_origin(origin='*',headers=['Content-Type'])
def tool_metadata():
    name = request.args.get('name')
    type_ = request.args.get('type')
    tool = tools_collection.find({'name': name, 'type': type_})
    tool = tool[0]
    
    tool = prepareToolMetadata(tool)

    resp = make_response(jsonify(tool), 200)

    return(resp)

# return JSON-LD of a tool given its metadata from the FAIR evaluator
@app.route('/tools/jsonld', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type'])
def tool_jsonld():
    try:
        tool = request.get_json()
        tool = tool['data']
        tool = prepareMetadataForEvaluation(tool)
        tool = build_json_ld(tool)
    except:
        data = {'Something went wrong when building the JSON-LD :('}
        resp = make_response(data, 400)
    else:
        resp = make_response(jsonify(tool), 200)

    return(resp)


## -------------------------------------------------- ##
##  SPDX and EDAM
## -------------------------------------------------- ##

# returns EDAM terms
@app.route('/EDAMTerms')
@cross_origin(origin='*',headers=['Content-Type'])
def EDAMTerms():
    try:
        EDAMVocabularyItems = prepareEDAM()
    except:
        data = {'Something went wrong when retrieving the EDAM vocabulary :('}
        resp = make_response(data, 400)

    else:
        resp = make_response(jsonify(EDAMVocabularyItems), 200)

    return resp

# returns SPDX licenses
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

# returns the URL of a given SPDX license identifier
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

# returns the SPDX license identifier that perfectly matches a given license name
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


## -------------------------------------------------- ##
##  FAIR evaluation
## -------------------------------------------------- ##

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

## -------------------------------------------------- ##
##  Badge
## -------------------------------------------------- ##
# Get badge for a tool given a URL to the tool's metadata
@app.route('/tool/badge', methods=['POST', 'GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def badge():
    badge = {
        "schemaVersion": 1,
        "label": "tool metadata",
        "message": "present",
        "color": "green",
        "logoSvg": "M91.2 132.3a20.2 20.2 0 0 1-15-16.5c-.5-2.8-.5-3.4 0-6.2a20 20 0 0 1 18.6-16.8c5-.3 8.5.7 12.6 3.3l2 1.3 5.2-2.6c3-1.4 5.4-2.7 5.5-2.9 0 0-.2-1.5-.7-3.2-1.9-7-2-16.2-.4-23.4l1-3.7c2.5-7.5 2.3-7.4 7-14.1l1.7-2c6.5-8.4 17-15 27.7-17.7l3.2-.8v-7l.2-7-1.9-.7a23.3 23.3 0 1 1 17.5.1l-1.9.8v6.5l-.2 6.5 1.3.2a50.2 50.2 0 0 1 41 71.6 51.4 51.4 0 0 1-55 27.6 53.3 53.3 0 0 1-35.5-23c-.1 0-2.4 1-5 2.4-4.2 2.1-4.6 2.4-4.4 3l.4 3.6c.4 5.8-1.6 11-5.8 15.3a18.4 18.4 0 0 1-9.2 5.3c-3 .8-7 .8-9.9.1zm9.6-9.2a11.4 11.4 0 0 0 3.2-18.4 11.5 11.5 0 0 0-18.5 3.5 14 14 0 0 0 0 9.1c1.5 3.1 4.7 5.7 8 6.6 2 .5 5.3.1 7.3-.8zm72.9-19.2 1.6-4.1c.8-2 .8-2.1 2.6-2.8l1.9-.7 3.7 1.5 4.2 1.5c.2 0 1.4-1 2.8-2.2 2.8-2.5 2.8-2 .6-6.9l-1.5-3.6.7-1.9c.6-1.4 1-1.7 2.3-2.2a86 86 0 0 0 4.1-1.7l2.6-1.2v-6.8l-4.1-1.6c-2.2-.9-4.2-1.7-4.3-2l-.8-1.7-.5-1.4 1.5-3.8c.9-2.1 1.5-4 1.5-4.3 0-.2-1.2-1.4-2.5-2.6l-2.4-2.3-1.8.7-4 1.7-2.3 1-1.8-.7c-1.3-.6-1.8-1-2.1-1.8l-1.8-4-1.3-2.8h-7.1l-1.2 2.7a93 93 0 0 0-1.6 4c-.3 1-.7 1.3-2.2 1.9l-1.8.7L155 55l-4.2-1.5c-.5 0-5.2 4.3-5.2 4.7l1.6 4.2 1.7 3.8-.7 1.7-.7 1.7-4 1.7-4 1.6-.2 3.5V80l2.3 1 4.2 1.6c1.6.5 1.8.7 2.4 2.3l.8 1.8-1.6 3.7-1.5 4.2c0 .4 1 1.6 2.3 2.9 2.7 2.5 2 2.5 7.2.3l3.4-1.5 1.8.7 1.8.7 1.4 3.5c2.2 5 1.8 4.8 5.7 4.8h3.3zM166 85a9 9 0 0 1-5.2-4.4c-.9-1.6-1-2.1-1-4.3 0-2.2.1-2.7 1-4.3a9.5 9.5 0 0 1 16.6 0c.8 1.5 1 2.2 1 4.3 0 2.2-.1 2.7-1 4.3a9.4 9.4 0 0 1-5.5 4.5c-2.3.6-3.7.6-5.9-.1zm4.1-81.6c8.3-2.2 12.3-12 8-19.4a13.1 13.1 0 1 0-8 19.3z"
    }
    resp = make_response(jsonify(badge), 201)
    return resp

@app.route('/tool/badge/test', methods=['POST', 'GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def badge_test():
    badge = {
        "schemaVersion": 1,
        "label": "tool metadata",
        "message": "present",
        "color": "green",
    }
    resp = make_response(jsonify(badge), 201)
    return resp


##--------------------------------------------------------------##
## Requests regarding docs in `tools_collection` collection
##--------------------------------------------------------------##

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
    
    

    


## ------------------------------------------##
##   START APP
## ------------------------------------------##

if __name__ == '__main__':
    app.run(debug=True, port=3000, ssl_context='adhoc')





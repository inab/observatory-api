
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
        "logoSvg": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNzUuOSIgaGVpZ2h0PSIzMTQuOSIgdmlld0JveD0iMCAwIDczIDgzLjMiPgogIDxwYXRoIGQ9Ik05OS4xIDY1LjMgOTAuNCA2MEM5MC4yIDYwIDgwIDc4LjMgODAgNzguNGMwIC4yIDkuNCA0LjggOS44IDQuOCAyLjctOC45IDQuMi0xMiA5LjItMTcuOXpNODkuNSA1Ni44bC05LjEtNS43YzAgLjEtMTMuMyAyMi41LTEzLjIgMjIuNmw5LjggNXoiIHN0eWxlPSJmaWxsOiNmZmY7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlLXdpZHRoOi4xODcyMDIiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02NyAtMzAuNCkiLz4KICA8cGF0aCBkPSJNNzIuMSA2MWMyLjMtNCA0LjItNyA0LjEtNy4xdi0uMWMtNSAxLjUtOCA3LjMtOC41IDExLjEtLjIgMS41IDAgMy43LjMgMy43TDcyIDYxeiIgc3R5bGU9ImZpbGw6I2ZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MDtzdHJva2UtZGFzaGFycmF5Om5vbmUiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02NyAtMzAuNCkiLz4KICA8ZyBzdHlsZT0iZmlsbDojZmZmIj4KICAgIDxwYXRoIGQ9Ik05MS4yIDEzMi4zYTIwLjIgMjAuMiAwIDAgMS0xNS0xNi41Yy0uNS0yLjgtLjUtMy40IDAtNi4yYTIwIDIwIDAgMCAxIDE4LjYtMTYuOGM1LS4zIDguNS43IDEyLjYgMy4zbDIgMS4zIDUuMi0yLjZjMy0xLjQgNS40LTIuNyA1LjUtMi45IDAgMC0uMi0xLjUtLjctMy4yLTEuOS03LTItMTYuMi0uNC0yMy40bDEtMy43YzIuNS03LjUgMi4zLTcuNCA3LTE0LjFsMS43LTJjNi41LTguNCAxNy0xNSAyNy43LTE3LjdsMy4yLS44di03bC4yLTctMS45LS43YTIzLjMgMjMuMyAwIDEgMSAxNy41LjFsLTEuOS44djYuNWwtLjIgNi41IDEuMy4yYTUwLjIgNTAuMiAwIDAgMSA0MSA3MS42IDUxLjQgNTEuNCAwIDAgMS01NSAyNy42IDUzLjMgNTMuMyAwIDAgMS0zNS41LTIzYy0uMSAwLTIuNCAxLTUgMi40LTQuMiAyLjEtNC42IDIuNC00LjQgM2wuNCAzLjZjLjQgNS44LTEuNiAxMS01LjggMTUuM2ExOC40IDE4LjQgMCAwIDEtOS4yIDUuM2MtMyAuOC03IC44LTkuOS4xem05LjYtOS4yYTExLjQgMTEuNCAwIDAgMCAzLjItMTguNCAxMS41IDExLjUgMCAwIDAtMTguNSAzLjUgMTQgMTQgMCAwIDAgMCA5LjFjMS41IDMuMSA0LjcgNS43IDggNi42IDIgLjUgNS4zLjEgNy4zLS44em03Mi45LTE5LjIgMS42LTQuMWMuOC0yIC44LTIuMSAyLjYtMi44bDEuOS0uNyAzLjcgMS41IDQuMiAxLjVjLjIgMCAxLjQtMSAyLjgtMi4yIDIuOC0yLjUgMi44LTIgLjYtNi45bC0xLjUtMy42LjctMS45Yy42LTEuNCAxLTEuNyAyLjMtMi4yYTg2IDg2IDAgMCAwIDQuMS0xLjdsMi42LTEuMnYtNi44bC00LjEtMS42Yy0yLjItLjktNC4yLTEuNy00LjMtMmwtLjgtMS43LS41LTEuNCAxLjUtMy44Yy45LTIuMSAxLjUtNCAxLjUtNC4zIDAtLjItMS4yLTEuNC0yLjUtMi42bC0yLjQtMi4zLTEuOC43LTQgMS43LTIuMyAxLTEuOC0uN2MtMS4zLS42LTEuOC0xLTIuMS0xLjhsLTEuOC00LTEuMy0yLjhoLTcuMWwtMS4yIDIuN2E5MyA5MyAwIDAgMC0xLjYgNGMtLjMgMS0uNyAxLjMtMi4yIDEuOWwtMS44LjdMMTU1IDU1bC00LjItMS41Yy0uNSAwLTUuMiA0LjMtNS4yIDQuN2wxLjYgNC4yIDEuNyAzLjgtLjcgMS43LS43IDEuNy00IDEuNy00IDEuNi0uMiAzLjVWODBsMi4zIDEgNC4yIDEuNmMxLjYuNSAxLjguNyAyLjQgMi4zbC44IDEuOC0xLjYgMy43LTEuNSA0LjJjMCAuNCAxIDEuNiAyLjMgMi45IDIuNyAyLjUgMiAyLjUgNy4yLjNsMy40LTEuNSAxLjguNyAxLjguNyAxLjQgMy41YzIuMiA1IDEuOCA0LjggNS43IDQuOGgzLjN6TTE2NiA4NWE5IDkgMCAwIDEtNS4yLTQuNGMtLjktMS42LTEtMi4xLTEtNC4zIDAtMi4yLjEtMi43IDEtNC4zYTkuNSA5LjUgMCAwIDEgMTYuNiAwYy44IDEuNSAxIDIuMiAxIDQuMyAwIDIuMi0uMSAyLjctMSA0LjNhOS40IDkuNCAwIDAgMS01LjUgNC41Yy0yLjMuNi0zLjcuNi01LjktLjF6bTQuMS04MS42YzguMy0yLjIgMTIuMy0xMiA4LTE5LjRhMTMuMSAxMy4xIDAgMSAwLTggMTkuM3oiIHN0eWxlPSJmaWxsOiNmZmY7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlLXdpZHRoOi4zMzIxOCIgdHJhbnNmb3JtPSJtYXRyaXgoLjUwMzY4IDAgMCAuNTAzNjggLTM4LjIgMTYuNCkiLz4KICA8L2c+Cjwvc3ZnPgo="
    }
    resp = make_response(jsonify(badge), 200)
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
    resp = make_response(jsonify(badge), 200)
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
    app.run(debug=True, port=3000)






import pymongo
import configparser

from pymongo import MongoClient
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS,cross_origin
import FAIRsoft
from FAIRsoft.indicators_evaluation.FAIR_indicators_eval import computeScores_from_list

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
discoverer_collection = connection['observatory2'][DISCOVERER]
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

def query_tools_type_source():
    '''
    Returns a list of dictionaries with name, type and sources of tools
    '''
    return list(discoverer_collection.find({},{'_id':0,'label':1,'type':1,'sources_labels':1}))


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

##################################
## Utils
##################################
def process_tool(tool):
    '''
    Processes a tool to return a dictionary with name, type and sources
    '''
    tool['label'] = tool['label'][0]
    
    return tool

@app.route('/tools/names_type_labels')
@cross_origin(origin='*',headers=['Content-Type'])
def names_type_labels():
    tools = list(discoverer_collection.find({},{'_id':0, '@id':1, 'label':1,'type':1,'sources_labels':1}))
    resp = []
    for tool in tools:
        resp.append(process_tool(tool))    
    return(resp)

@app.route('/tools')
@cross_origin(origin='*',headers=['Content-Type'])
def tool_metadata():
    id_ = request.args.get('id')
    tool = tools_collection.find({'@id':id_})
    tool = tool[0]
    tool.pop('_id')
    resp = make_response(jsonify(tool), 200)
     
    return(resp)

# Evaluate FAIRness of a tool given its metadata
# TODO: complete
@app.route('/tools/evaluate')
@cross_origin(origin='*',headers=['Content-Type'])
def evaluate():
    data = request.get_json()
    if data:
        # TODO:
        # Evaluate metadata
        pass
    else:
        data = {'message': 'No tool id or metadata provided', 'code': 'ERROR'}
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
@app.route('/tools', methods=['GET'])
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





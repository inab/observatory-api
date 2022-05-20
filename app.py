
import pymongo
import configparser

from pymongo import MongoClient
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS,cross_origin

# connecting to db
config = configparser.ConfigParser()
config.read('config_db.ini')
DBHOST = config['MONGO_DETAILS']['DBHOST']
DBPORT = config['MONGO_DETAILS']['DBPORT']
DATABASE = config['MONGO_DETAILS']['DATABASE']
TOOLS = config['MONGO_DETAILS']['TOOLS']
ALAMBIQUE = config['MONGO_DETAILS']['ALAMBIQUE']
STATS = config['MONGO_DETAILS']['STATS']

connection = MongoClient(DBHOST, int(DBPORT))
collection = connection[DATABASE][TOOLS]
stats = connection[DATABASE][STATS]

def latest_count():
    record = list(stats.find({
        "variable":"tools_counts_per_source"
        }).sort("version",-1).limit(1))
    return(record)

def version_count(version):
    try:
        record = list(stats.find({
            "variable":"tools_counts_per_source",
            "version":version}))
    except Exception:
        return(Exception)
    else:
        return(record)

def total_count():
    record = list(stats.find({"variable":"tools_count"}).sort("version",-1).limit(1))
    return(record)

        
## Init app
app = Flask(__name__)

## CORS
CORS(app,resources={r"/api": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


def process_request(action, parameters):
    try:
        data = action(parameters)
        
    except Exception as err:
        resp = make_response(err, 400)
        print(err)
    else:
        data = data
        resp = make_response(jsonify(data), 201)
    finally:
        return resp

def action_count_total(parameters):
    try:
        docs=total_count()
    except Exception as err:
        return(str(err))
    else:
        [entry.pop('_id') for entry in docs]
    return(docs)

    

def action_counts_source(parameters):
    try:
        if request.args.get('version'):
            if request.args.get('version') == 'latest':
                docs = latest_count()
            else:
                version = request.args.get('version'+1)
                docs = version_count(version)
        else:
            docs = latest_count()

    except Exception as err:
        return(('An error occurred while trying to fetch your queried data.'
                ' Please, check the version in your query and retry.'
                f' Error message: {str(err)}'))
    else:
        print(docs)
        [entry.pop('_id') for entry in docs]
    return(docs)


@app.route('/stats/tool/count_per_source')
def counts_per_source():
    resp = process_request(action_counts_source, request.args)
    return(resp)


@app.route('/stats/tool/count_total')
def count_total():
    resp = process_request(action_count_total, request.args)
    return(resp)


@app.route('/tools', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def tools():
    try:
        tools = []
        [tools.append(entry) for entry in collection.find({})]
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

@app.route('/tool/description', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type'])
def description():
    try:
        tool_name = request.args.get('name')
        entry = collection.find_one({'name' : tool_name})
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

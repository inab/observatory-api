from app.helpers.database import connect_DB 
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB

tools_collection, stats = connect_DB()

def process_request(action, parameters):
    try:
        data = action(parameters)
    except Exception as err:
        print(f'Error here {err}')
        raise HTTPException(status_code=400, detail=str(err))
    else:
        return JSONResponse(content=data, status_code=201)

def query(func):
    '''
    Error handling of query execution and removal of _id field
    '''
    async def wrapper(*args, **kwargs):
        try:
            docs = await func(*args, **kwargs)
        except Exception as err:
            raise HTTPException(status_code=400, detail=str(err))
        else:
            [entry.pop('_id', None) for entry in docs]

        if len(docs) == 0:
            return 'No results found'
        elif len(docs) == 1:
            return docs[0]
        else:
            return docs

    return wrapper

def clean_quotations(string: str) -> str:
    return string.replace('"', '').replace("'", '')

def prep_parameters(parameters: dict) -> tuple:
    '''
    If version not stated, assign `latest` version
    If collection not stated, assign `tools` collection
    '''
    try:
        version = clean_quotations(parameters.get('version', 'latest'))
        collection = clean_quotations(parameters.get('collection', 'tools'))
    except Exception as err:
        raise HTTPException(status_code=400, detail=(
            'An error occurred while trying to read query parameters. '
            'Please, check version and collection in your query and retry. '
            f'Error message: {str(err)}'))
    else:
        return collection, version

@query
async def make_query(variable_name: str, parameters: dict):
    collection, version = prep_parameters(parameters)
    if version == 'latest':
        record = list(stats.find({
            "variable": variable_name,
            "collection": collection,
        }).sort("version", -1).limit(1))
    else:
        record = list(stats.find({
            "variable": variable_name,
            "collection": collection,
            "version": version
        }))
    return record
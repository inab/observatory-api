from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.helpers.search import make_search, calculate_stats
from app.helpers.utils import prepare_sources_labels
from app.helpers.EDAM_forFE import EDAMDict
import re

router = APIRouter()

@router.get('/search', tags=["search"])
async def search(request: Request):
    try:
        tools = {}
        counts = {
            'name': 0,
            'description': 0,
            'topics': 0,
            'operations': 0,
            'publication_title': 0,
            'publication_abstract': 0,
        }

        search = {}
        params = request.query_params

        if source := params.get('source'):
            search['source'] = {'$in': source.split(',')}

        if type_ := params.get('type'):
            search['type'] = {'$in': type_.split(',')}

        if topics := params.get('topics'):
            search['topics.uri'] = {'$in': topics.split(',')}

        if operations := params.get('operations'):
            search['operations.uri'] = {'$in': operations.split(',')}

        if license := params.get('license'):
            search['license.name'] = {'$in': license.split(',')}

        if collections := params.get('tags'):
            search['tags'] = {'$in': collections.split(',')}

        if input := params.get('input_format'):
            search['input.term'] = {'$in': input.split(',')}

        if output := params.get('output_format'):
            search['output.term'] = {'$in': output.split(',')}

        q = params.get('q')
        pat = re.compile(rf'{q}', re.I)

        search_in = params.get('searchIn', '').split(',')
        if search_in:
            if 'name' in search_in:
                tools, counts = make_search('name', 'name', {'$regex': pat}, search, tools, counts)

            if 'description' in search_in:
                tools, counts = make_search('description', 'description', {'$regex': pat}, search, tools, counts)

            if 'topics' in search_in:
                edam_ids = [key for key, value in EDAMDict.items() if re.search(pat, value)]
                tools, counts = make_search('topics', 'edam_topics', {'$in': edam_ids}, search, tools, counts)

            if 'operations' in search_in:
                edam_ids = [key for key, value in EDAMDict.items() if re.search(pat, value)]
                tools, counts = make_search('operations', 'edam_operations', {'$in': edam_ids}, search, tools, counts)
        else:
            tools, counts = make_search('name', 'name', {'$regex': pat}, search, tools, counts)
            tools, counts = make_search('description', 'description', {'$regex': pat}, search, tools, counts)
            edam_ids = [key for key, value in EDAMDict.items() if re.search(pat, value)]
            tools, counts = make_search('topics', 'edam_topics', {'$in': edam_ids}, search, tools, counts)
            tools, counts = make_search('operations', 'edam_operations', {'$in': edam_ids}, search, tools, counts)

        tools = list(tools.values())
        tools = [prepare_sources_labels(tool) for tool in tools]
        stats = calculate_stats(tools)
        page = int(params.get('page', 0))
        a = page * 10
        b = page * 10 + 10

        data = {
            'query': q,
            'tools': tools[a:b],
            'total_tools': len(tools),
            'counts': counts,
            'stats': stats,
        }

    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Something went wrong while fetching: {err}")

    return JSONResponse(content=data)

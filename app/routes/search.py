from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict, List
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB
from app.helpers.search import make_search, calculate_stats, calculate_total_stats
from app.helpers.utils import prepare_sources_labels, prepareToolMetadata
import re
from bson import ObjectId 

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
                tools, counts = make_search('name', 'data.name', {'$regex': pat}, search, tools, counts)

            if 'description' in search_in:
                tools, counts = make_search('description', 'data.description', {'$regex': pat}, search, tools, counts)

            if 'topics' in search_in:
                tools, counts = make_search('topics', 'data.topics.term', {'$regex': pat}, search, tools, counts)

            if 'operations' in search_in:
                tools, counts = make_search('operations', 'data.operations.term', {'$regex': pat}, search, tools, counts)
        else:
            tools, counts = make_search('name', 'data.name', {'$regex': pat}, search, tools, counts)
            tools, counts = make_search('description', 'data.description', {'$regex': pat}, search, tools, counts)
            tools, counts = make_search('topics', 'data.topics.term', {'$regex': pat}, search, tools, counts)
            tools, counts = make_search('operations', 'data.operations.term', {'$regex': pat}, search, tools, counts)

        tools = list(tools.values())

        _, stats_collection, pubs_collection, _ = connect_DB()
        _hydrate_publications(tools, pubs_collection)
        _hydrate_fairsoft(tools, stats_collection)

        tools = [prepare_sources_labels(tool) for tool in tools]
        tools = [prepareToolMetadata(tool) for tool in tools]
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
        raise
        #raise HTTPException(status_code=400, detail=f"Something went wrong while fetching: {err}")

    return JSONResponse(content=data)



def _hydrate_publications(tools: List[Dict[str, Any]], pubs_collection) -> None:
    """In-place: each tool's 'publication' list of ObjectIds becomes a list of publication.data dicts."""
    pub_ids = set()
    for tool in tools:
        for pid in (tool.get('publication') or []):
            if pid is not None:
                try:
                    pub_ids.add(ObjectId(pid))
                except Exception:
                    pass

    if not pub_ids:
        return

    pub_map = {
        str(p["_id"]): p.get("data")
        for p in pubs_collection.find(
            {"_id": {"$in": list(pub_ids)}},
            projection={"_id": 1, "data": 1},
        )
    }

    for tool in tools:
        pub_list = tool.get('publication') or []
        if not isinstance(pub_list, list):
            tool['publication'] = []
            continue
        tool['publication'] = [
            pub_map[str(ObjectId(pid))]
            for pid in pub_list
            if pid is not None and str(ObjectId(pid)) in pub_map
        ]


def _hydrate_fairsoft(tools: List[Dict[str, Any]], stats_collection) -> None:
    """In-place: add 'fairsoft' key to each tool from the stats collection."""
    tool_ids = [tool['id'] for tool in tools if tool.get('id')]

    if not tool_ids:
        return

    fairsoft_map: Dict[str, Any] = {}
    for doc in stats_collection.find(
        {"createdFrom": {"$in": tool_ids}, "variable": "FAIR_scores"},
        projection={"createdFrom": 1, "data": 1},
    ):
        for tid in doc.get("createdFrom", []):
            if tid in tool_ids:
                fairsoft_map[tid] = doc.get("data")

    for tool in tools:
        tid = tool.get('id')
        tool['fairsoft'] = fairsoft_map.get(tid)


def _jsonify_mongo(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: _jsonify_mongo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonify_mongo(v) for v in value]
    return value


@router.get("/initial-search", tags=["search"])
async def initial_search(request: Request):
    tools_collection, stats_collection, pubs_collection, _ = connect_DB()

    params = request.query_params
    page = int(params.get('page', 0))
    page_size = 10

    filters: Dict[str, Any] = {}
    if source := params.get('source'):
        filters['data.source'] = {'$in': source.split(',')}
    if type_ := params.get('type'):
        filters['data.type'] = {'$in': type_.split(',')}
    if topics := params.get('topics'):
        filters['data.topics.uri'] = {'$in': topics.split(',')}
    if operations := params.get('operations'):
        filters['data.operations.uri'] = {'$in': operations.split(',')}
    if license_ := params.get('license'):
        filters['data.license.name'] = {'$in': license_.split(',')}
    if tags := params.get('tags'):
        filters['data.tags'] = {'$in': tags.split(',')}
    if input_fmt := params.get('input_format'):
        filters['data.input.term'] = {'$in': input_fmt.split(',')}
    if output_fmt := params.get('output_format'):
        filters['data.output.term'] = {'$in': output_fmt.split(',')}

    # Score each tool by completeness so richer, more validated tools surface first.
    score_expr: Dict[str, Any] = {
        '$add': [
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.publication', []]}}, 0]}, 3, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.webpage', []]}}, 0]}, 2, 0]},
            {'$size': {'$ifNull': ['$data.source', []]}},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.topics', []]}}, 0]}, 1, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.operations', []]}}, 0]}, 1, 0]},
            {'$cond': [{'$ifNull': ['$data.inst_instr', False]}, 1, 0]},
        ]
    }

    pipeline = [
        {'$match': filters},
        {'$addFields': {'_score': score_expr}},
        {'$sort': {'_score': -1, '_id': 1}},
        {'$facet': {
            'total': [{'$count': 'count'}],
            'tools': [
                {'$skip': page * page_size},
                {'$limit': page_size},
                {'$project': {'_score': 0}},
            ],
        }},
    ]

    result = list(tools_collection.aggregate(pipeline))
    facet = result[0]
    total = facet['total'][0]['count'] if facet['total'] else 0

    tools_data = []
    for doc in facet['tools']:
        tool = doc.get('data', {})
        tool['id'] = str(doc['_id'])
        tools_data.append(tool)

    _hydrate_publications(tools_data, pubs_collection)
    _hydrate_fairsoft(tools_data, stats_collection)

    return JSONResponse(content=_jsonify_mongo({
        'query': '',
        'tools': tools_data,
        'total_tools': total,
        'page': page,
        'stats': calculate_total_stats(),
    }))
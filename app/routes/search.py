from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict, List
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB
from app.helpers.search import calculate_stats, calculate_total_stats
from app.helpers.utils import prepare_sources_labels, prepareToolMetadata
from bson import ObjectId

router = APIRouter()


def _build_filters(params) -> Dict[str, Any]:
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
    return filters


@router.get('/search', tags=["search"])
async def search(request: Request):
    tools_collection, stats_collection, pubs_collection, _ = connect_DB()

    params = request.query_params
    q = params.get('q')
    page = int(params.get('page', 0))
    page_size = 10

    filters = _build_filters(params)

    if q:
        match: Dict[str, Any] = {'$text': {'$search': q}, **filters}
        add_score = {'$addFields': {'_score': {'$meta': 'textScore'}}}
        sort_stage = {'$sort': {'_score': -1, '_id': 1}}
    else:
        match = filters
        add_score = {'$addFields': {'_score': 0}}
        sort_stage = {'$sort': {'_id': 1}}

    pipeline = [
        {'$match': match},
        add_score,
        sort_stage,
        {'$facet': {
            'total': [{'$count': 'count'}],
            # Lightweight projection over all matching docs for facet stats
            'stats_docs': [{'$project': {
                'data.type': 1, 'data.source': 1, 'data.edam_topics': 1,
                'data.edam_operations': 1, 'data.license': 1,
                'data.input': 1, 'data.output': 1, 'data.tags': 1,
            }}],
            # Full documents for the requested page only
            'tools': [
                {'$skip': page * page_size},
                {'$limit': page_size},
                {'$project': {'_score': 0}},
            ],
        }},
    ]

    result = list(tools_collection.aggregate(pipeline))[0]
    total = result['total'][0]['count'] if result['total'] else 0
    stats_data = [doc['data'] for doc in result['stats_docs']]
    search_stats = calculate_stats(stats_data)

    tools_data = []
    for doc in result['tools']:
        tool = doc.get('data', {})
        tool['id'] = str(doc['_id'])
        tools_data.append(tool)

    _hydrate_publications(tools_data, pubs_collection)
    _hydrate_fairsoft(tools_data, stats_collection)
    tools_data = [prepare_sources_labels(t) for t in tools_data]
    tools_data = [prepareToolMetadata(t) for t in tools_data]

    return JSONResponse(content=_jsonify_mongo({
        'query': q,
        'tools': tools_data,
        'total_tools': total,
        'stats': search_stats,
    }))



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

    filters = _build_filters(params)

    total = tools_collection.count_documents(filters)
    docs = tools_collection.find(filters).sort('_id', 1).skip(page * page_size).limit(page_size)

    tools_data = []
    for doc in docs:
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
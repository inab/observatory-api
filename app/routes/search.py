from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB
from app.helpers.search import calculate_stats, calculate_total_stats
from app.helpers.utils import prepare_sources_labels, prepareToolMetadata, hydrate_fairsoft, clean_edam_terms
from bson import ObjectId

router = APIRouter()

# Case-insensitive collation. Used for the topic/operation term filters so the matching
# is case-insensitive *and* index-backed: a plain regex (`$options: 'i'`) forces a full
# collection scan, whereas exact `$in` equality under this collation uses a matching
# collation index (see TERM_COLLATION in scripts/create_indexes.py). Only passed on
# queries that actually filter by term, since a collation also disables the plain binary
# indexes (source/type/license/...) for that request.
TERM_COLLATION = {'locale': 'en', 'strength': 2}


def _term_match(values: str) -> Dict[str, Any]:
    """Match EDAM terms by exact value, tolerating the leading-quote artefact.

    Some stored terms carry a leading double-quote (e.g. '"Allergy'); the stats facet
    strips it before exposing terms, so callers send the cleaned value. Matching both the
    bare and leading-quoted forms covers it. Case-insensitivity comes from TERM_COLLATION,
    not from this predicate, so the match stays index-friendly.
    """
    variants = []
    for v in values.split(','):
        variants.append(v)
        variants.append('"' + v)
    return {'$in': variants}


def _build_filters(
    source: Optional[str],
    type_: Optional[str],
    topics: Optional[str],
    operations: Optional[str],
    license_: Optional[str],
    tags: Optional[str],
    input_format: Optional[str],
    output_format: Optional[str],
) -> Dict[str, Any]:
    filters: Dict[str, Any] = {}
    if source:
        source = source.replace('bioconda_recipes','bioconda')
        source = source.replace('bioconda','bioconda_recipes')
        print(source)
        filters['data.source'] = {'$in': source.split(',')}
    if type_:
        filters['data.type'] = {'$in': type_.split(',')}
    if topics:
        filters['data.topics.term'] = _term_match(topics)
    if operations:
        filters['data.operations.term'] = _term_match(operations)
    if license_:
        filters['data.license.name'] = {'$in': license_.split(',')}
    if tags:
        filters['data.tags'] = {'$in': tags.split(',')}
    if input_format:
        filters['data.input.term'] = {'$in': input_format.split(',')}
    if output_format:
        filters['data.output.term'] = {'$in': output_format.split(',')}
    return filters


@router.get('/search', tags=["search"])
async def search(
    q: Optional[str] = Query(None, description="Text search query"),
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    source: Optional[str] = Query(None, description="Comma-separated source names"),
    type: Optional[str] = Query(None, alias="type", description="Comma-separated tool types"),
    topics: Optional[str] = Query(None, description="Comma-separated topic terms"),
    operations: Optional[str] = Query(None, description="Comma-separated operation terms"),
    license: Optional[str] = Query(None, alias="license", description="Comma-separated license names"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    input_format: Optional[str] = Query(None, description="Comma-separated input format terms"),
    output_format: Optional[str] = Query(None, description="Comma-separated output format terms"),
):
    tools_collection, stats_collection, pubs_collection, _ = connect_DB()

    page_size = 10
    filters = _build_filters(source, type, topics, operations, license, tags, input_format, output_format)
    # Only apply the case-insensitive collation when a term filter is present; otherwise it
    # would needlessly disable the plain binary indexes used by the other filters.
    collation = TERM_COLLATION if (topics or operations) else None

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
            # Full documents for the requested page only
            'tools': [
                {'$skip': page * page_size},
                {'$limit': page_size},
                {'$project': {'_score': 0}},
            ],
        }},
    ]

    result = list(tools_collection.aggregate(pipeline, collation=collation))[0]
    total = result['total'][0]['count'] if result['total'] else 0

    # Stats are computed from a separate streaming cursor rather than inside the
    # $facet above: a $facet emits all its output in a single document, which is
    # capped at 16MB, so projecting every matching doc into a facet overflows for
    # broad queries (BSONObjectTooLarge). A cursor streams in batches with no such
    # ceiling. find() supports $text, so the same match works for both branches.
    stats_cursor = tools_collection.find(
        match,
        projection={
            'data.type': 1, 'data.source': 1, 'data.topics': 1,
            'data.operations': 1, 'data.license': 1,
            'data.input': 1, 'data.output': 1, 'data.tags': 1,
        },
        collation=collation,
    )
    search_stats = calculate_stats([doc['data'] for doc in stats_cursor])

    tools_data = []
    for doc in result['tools']:
        tool = doc.get('data', {})
        tool['id'] = str(doc['_id'])
        tools_data.append(tool)

    for t in tools_data:
        clean_edam_terms(t)
    _hydrate_publications(tools_data, pubs_collection)
    hydrate_fairsoft(tools_data, stats_collection)
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


def _jsonify_mongo(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: _jsonify_mongo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonify_mongo(v) for v in value]
    return value


@router.get("/initial-search", tags=["search"])
async def initial_search(
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    source: Optional[str] = Query(None, description="Comma-separated source names"),
    type: Optional[str] = Query(None, alias="type", description="Comma-separated tool types"),
    topics: Optional[str] = Query(None, description="Comma-separated topic terms"),
    operations: Optional[str] = Query(None, description="Comma-separated operation terms"),
    license: Optional[str] = Query(None, alias="license", description="Comma-separated license names"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    input_format: Optional[str] = Query(None, description="Comma-separated input format terms"),
    output_format: Optional[str] = Query(None, description="Comma-separated output format terms"),
):
    tools_collection, stats_collection, pubs_collection, _ = connect_DB()

    page_size = 10

    filters = _build_filters(source, type, topics, operations, license, tags, input_format, output_format)
    collation = TERM_COLLATION if (topics or operations) else None

    total = tools_collection.count_documents(filters, collation=collation)

    pipeline = [
        {'$match': filters},
        {'$addFields': {'_score': {'$add': [
            # description is a list; weight it highest
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.description', []]}}, 0]}, 4, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.topics', []]}}, 0]}, 1, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.operations', []]}}, 0]}, 1, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.webpage', []]}}, 0]}, 1, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.publication', []]}}, 0]}, 1, 0]},
            {'$cond': [{'$gt': [{'$size': {'$ifNull': ['$data.source', []]}}, 1]}, 1, 0]},
        ]}}},
        {'$sort': {'_score': -1, '_id': 1}},
        {'$skip': page * page_size},
        {'$limit': page_size},
        {'$project': {'_score': 0}},
    ]

    tools_data = []
    for doc in tools_collection.aggregate(pipeline, collation=collation):
        tool = doc.get('data', {})
        tool['id'] = str(doc['_id'])
        tools_data.append(tool)

    for t in tools_data:
        clean_edam_terms(t)
    _hydrate_publications(tools_data, pubs_collection)
    hydrate_fairsoft(tools_data, stats_collection)

    return JSONResponse(content=_jsonify_mongo({
        'query': '',
        'tools': tools_data,
        'total_tools': total,
        'page': page,
        'stats': calculate_total_stats(),
    }))
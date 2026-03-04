from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict, List
from fastapi.responses import JSONResponse
from app.helpers.database import connect_DB
from app.helpers.search import make_search, calculate_stats
from app.helpers.utils import prepare_sources_labels, prepareToolMetadata
from app.helpers.EDAM_forFE import EDAMDict
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
                edam_ids = [key for key, value in EDAMDict.items() if re.search(pat, value)]
                tools, counts = make_search('topics', 'data.edam_topics', {'$in': edam_ids}, search, tools, counts)

            if 'operations' in search_in:
                edam_ids = [key for key, value in EDAMDict.items() if re.search(pat, value)]
                tools, counts = make_search('operations', 'data.edam_operations', {'$in': edam_ids}, search, tools, counts)
        else:
            tools, counts = make_search('name', 'data.name', {'$regex': pat}, search, tools, counts)
            tools, counts = make_search('description', 'data.description', {'$regex': pat}, search, tools, counts)
            edam_ids = [key for key, value in EDAMDict.items() if re.search(pat, value)]
            tools, counts = make_search('topics', 'data.edam_topics', {'$in': edam_ids}, search, tools, counts)
            tools, counts = make_search('perations', 'data.edam_operations', {'$in': edam_ids}, search, tools, counts)

        tools = list(tools.values())
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


RELEVANT_TYPES = {"rest", "web", "app", "suite", "workbench", "db", "soap", "sparql"}


def _projection_for_cards() -> Dict[str, int]:
    # Keep _id only for internal dedupe; we will drop it from the response.
    return {
        "_id": 1,
        "data": 1,  # simplest: keep whole data blob
        # If data is huge and you want to slim it down, replace with specific fields.
    }


def _base_match(extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    match: Dict[str, Any] = {
        "data.name": {"$exists": True, "$ne": ""},
        "data.description": {"$exists": True, "$ne": ""},
        "data.webpage": {"$exists": True, "$type": "array", "$ne": []},
        "data.type": {"$in": list(RELEVANT_TYPES)},
    }
    if extra:
        match.update(extra)
    return match


def _dedupe_by_id(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for d in docs:
        _id = d.get("_id")
        if _id in seen:
            continue
        seen.add(_id)
        out.append(d)
    return out


def _hydrate_publications_in_data(
    tools_docs: List[Dict[str, Any]], pubs_collection
) -> None:
    """In-place: tools_docs[i]['data']['publication'] becomes list of publication.data dicts."""
    pub_ids: Set[Any] = set()

    for doc in tools_docs:
        data = doc.get("data") or {}
        pub_list = data.get("publication") or []
        if isinstance(pub_list, list):
            for pid in pub_list:
                if pid is not None:
                    pub_ids.add(pid)

    if not pub_ids:
        # normalize to []
        for doc in tools_docs:
            data = doc.setdefault("data", {})
            if not isinstance(data.get("publication"), list):
                data["publication"] = []
        return

    cursor = pubs_collection.find(
        {"_id": {"$in": list(pub_ids)}},
        projection={"_id": 1, "data": 1},
    )
    pub_map: Dict[Any, Any] = {p["_id"]: p.get("data") for p in cursor}

    for doc in tools_docs:
        data = doc.setdefault("data", {})
        pub_list = data.get("publication") or []
        if not isinstance(pub_list, list):
            data["publication"] = []
            continue
        data["publication"] = [
            pub_map[pid] for pid in pub_list if pid in pub_map and pub_map[pid] is not None
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
async def initial_search():
    tools_collection, stats, pubs_collection, availability_collection = connect_DB()

    target_n = 10
    projection = _projection_for_cards()
    selected: List[Dict[str, Any]] = []

    # 1) Diversity pass (1 per type)
    for t in sorted(RELEVANT_TYPES):
        if len(selected) >= target_n:
            break
        pipeline = [
            {"$match": _base_match({"data.type": t})},
            {"$sample": {"size": 1}},
            {"$project": projection},
        ]
        selected.extend(list(tools_collection.aggregate(pipeline)))

    selected = _dedupe_by_id(selected)

    # 2) Fill remaining constrained
    remaining = target_n - len(selected)
    if remaining > 0:
        exclude_ids = [d["_id"] for d in selected if "_id" in d]
        pipeline = [
            {"$match": _base_match({"_id": {"$nin": exclude_ids}})},
            {"$sample": {"size": remaining}},
            {"$project": projection},
        ]
        selected.extend(list(tools_collection.aggregate(pipeline)))
        selected = _dedupe_by_id(selected)

    # 3) Fallback relax
    remaining = target_n - len(selected)
    if remaining > 0:
        exclude_ids = [d["_id"] for d in selected if "_id" in d]
        pipeline = [
            {"$match": {"_id": {"$nin": exclude_ids}}},
            {"$sample": {"size": remaining}},
            {"$project": projection},
        ]
        selected.extend(list(tools_collection.aggregate(pipeline)))
        selected = _dedupe_by_id(selected)

    # Hydrate publications inside data
    _hydrate_publications_in_data(selected, pubs_collection)

    # Return only the data payloads
    tools_data = [doc.get("data", {}) for doc in selected]

    return _jsonify_mongo(
        {
            "query": "",
            "totalTools": len(tools_data),
            "tools": tools_data,
            "note": "Initial sample (constrained-random, diverse + reasonably complete).",
        }
    )
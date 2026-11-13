"""GET /semantic-search: the hybrid semantic search (app/services/semantic_search).

Same params (minus searchIn) and response shape as /search. Rank, then filter: the
hybrid returns its top CANDIDATES tools, MongoDB keeps those that pass the filters,
and pagination, `total_tools` and `stats` are over what's left, in the hybrid's order.
So results stop at CANDIDATES (default 200, env/ini `SEMANTIC_SEARCH_CANDIDATES`).
"""

import logging
from functools import cache
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.helpers.database import connect_DB
from app.helpers.search import calculate_stats
from app.routes.search import TERM_COLLATION, _build_filters, _finalize_tools, _jsonify_mongo
from app.services.semantic_search import hybrid
from app.services.semantic_search.index import enabled, setting

logger = logging.getLogger(__name__)

router = APIRouter()

PAGE_SIZE = 10
STATS_PROJECTION = {
    'data.type': 1, 'data.source': 1, 'data.topics': 1,
    'data.operations': 1, 'data.license': 1,
    'data.input': 1, 'data.output': 1, 'data.tags': 1,
}


def candidates() -> int:
    return int(setting('SEMANTIC_SEARCH_CANDIDATES', '200'))


@cache
def _collections():
    """One MongoClient for this router, created on first use (not at import)."""
    tools, stats, pubs, _ = connect_DB()
    return tools, stats, pubs


def _object_ids(hits: List[hybrid.FusedHit]) -> List[ObjectId]:
    ids = []
    for h in hits:
        try:
            ids.append(ObjectId(h.tool_id))
        except (InvalidId, TypeError):
            logger.warning("semantic search: index has a non-ObjectId tool_id %r", h.tool_id)
    return ids


EXAMPLE = {
    "query": "remove haplotigs from a diploid assembly",
    "tools": [{
        "id": "69e772c4c0cec6c6a36fa065",
        "name": "purge_haplotigs",
        "type": ["cmd"],
        "semantic_score": 0.0487,
        "ranks": {"dense_description": 1, "bm25_description": 2, "bm25_names": 1, "dense_queries": 2},
        "...": "the same tool metadata as /search",
    }],
    "total_tools": 200,
    "page": 0,
    "stats": {"...": "same facets as /search, over the filtered results"},
}


@router.get(
    '/semantic-search',
    tags=["search"],
    summary="Find software from a description of the task, or by name",
    responses={
        200: {"description": "A page of tools, best match first",
              "content": {"application/json": {"example": EXAMPLE}}},
        400: {"description": "`q` is blank"},
        503: {"description": "Semantic search is disabled on this server, or its index is unreachable"},
    },
)
async def semantic_search(
    q: str = Query(
        ...,
        description=("What the software should do, in plain words (\"align long reads to a "
                     "reference\"), or the tool's name (\"samtools\")."),
        examples=["remove haplotigs from a diploid assembly"],
    ),
    page: int = Query(0, ge=0, description="Page number (0-indexed, 10 tools per page)"),
    source: Optional[str] = Query(None, description="Comma-separated source names"),
    type: Optional[str] = Query(None, alias="type", description="Comma-separated tool types"),
    topics: Optional[str] = Query(None, description="Comma-separated topic terms"),
    operations: Optional[str] = Query(None, description="Comma-separated operation terms"),
    license: Optional[str] = Query(None, alias="license", description="Comma-separated license names"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    input_format: Optional[str] = Query(None, description="Comma-separated input format terms"),
    output_format: Optional[str] = Query(None, description="Comma-separated output format terms"),
):
    """
    Unlike `/search`, which matches keywords, this search understands what the query
    asks for: "remove haplotigs from a diploid assembly" finds purge_haplotigs and
    purge_dups even though neither description uses those exact words. A query that is
    a tool's name puts that tool first.

    It combines four rankings: meaning and keywords in tool descriptions, keywords in
    tool names, and meaning in example queries written for each tool.

    **Filters and totals.** Only the best 200 tools for the query are considered. The
    filters are applied to those, so `total_tools` is at most 200 and `stats` describes
    the filtered set. Results keep the search's order.

    **Response.** The same shape as `/search`. Each tool also has:

    - `semantic_score`: its combined score (higher is better; only comparable within one query).
    - `ranks`: its rank in each of the four rankings that returned it, for debugging.
    """
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="q must not be blank")
    if not enabled():
        raise HTTPException(status_code=503, detail="Semantic search is disabled on this server")

    try:
        # Sync (Qdrant client + CPU encoding): off the event loop.
        hits = await run_in_threadpool(hybrid.search, q, candidates())
    except hybrid.SearchUnavailable as err:
        logger.error("%s", err)
        raise HTTPException(status_code=503, detail="Semantic search index is unavailable")

    by_id = {str(h.tool_id): h for h in hits}
    tools_collection, stats_collection, pubs_collection = _collections()
    filters = _build_filters(source, type, topics, operations, license, tags, input_format, output_format)
    collation = TERM_COLLATION if (topics or operations) else None
    match = {'_id': {'$in': _object_ids(hits)}, **filters}

    # Light pass over every candidate that passes the filters: order + stats.
    kept: Dict[str, Dict[str, Any]] = {
        str(doc['_id']): doc.get('data', {})
        for doc in tools_collection.find(match, projection=STATS_PROJECTION, collation=collation)
    }
    ordered = [h for h in hits if h.tool_id in kept]
    search_stats = calculate_stats([kept[h.tool_id] for h in ordered])

    # Full documents for the requested page only.
    page_hits = ordered[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    docs = {
        str(doc['_id']): doc
        for doc in tools_collection.find({'_id': {'$in': _object_ids(page_hits)}})
    }
    tools_data = []
    for h in page_hits:
        doc = docs.get(h.tool_id)
        if doc is None:  # removed between the two reads
            continue
        tool = doc.get('data', {})
        tool['id'] = h.tool_id
        tools_data.append(tool)

    tools_data = _finalize_tools(tools_data, pubs_collection, stats_collection)
    for tool in tools_data:
        h = by_id[tool['id']]
        tool['semantic_score'] = h.score
        tool['ranks'] = h.ranks

    return JSONResponse(content=_jsonify_mongo({
        'query': q,
        'tools': tools_data,
        'total_tools': len(ordered),
        'page': page,
        'stats': search_stats,
    }))

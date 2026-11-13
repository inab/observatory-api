"""The four retrievers of the hybrid search, and the name-match rule.

Ported from search-eval `retrieval/{dense_description,bm25_description,bm25_names,dense_queries}.py`.

1. dense_description: cosine between the query and each tool's description point.
2. bm25_description: BM25 (Qdrant's `qdrant/bm25`, stemming + stopwords) over names,
   descriptions and EDAM terms.
3. bm25_names: BM25 over names and labels only (`tool_search_exp_names`), no stemming
   or stopwords, so "STAR" doesn't match "stars".
4. dense_queries: cosine against the LLM-written synthetic queries, grouped by tool.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from app.services.semantic_search.index import (
    Hit, client, collection, encode, kind_filter, names_collection, to_hit,
)

PAYLOAD = ["tool_id", "name", "kind", "text"]


def _name_bm25_options():
    """
    MUST match the pipeline's NAME_BM25_OPTIONS
    (research-software-etl src/infrastructure/db/qdrant/tool_search_index.py), or the
    query tokens won't hash to the indexed ones. Copied rather than imported to keep the
    pipeline out of the API's dependencies.
    """
    from qdrant_client import models

    return models.Bm25Config(
        stopwords=models.StopwordsSet(languages=[], custom=[]),
        stemmer=models.DisabledStemmerParams(type=models.NoStemmer.NONE),
        avg_len=3.0,
    )


def dense_description(query: str, k: int = 10) -> list[Hit]:
    """The k tools whose description is closest to the query, best first."""
    result = client().query_points(
        collection(),
        query=list(encode(query)),
        using="dense",
        query_filter=kind_filter("description"),
        limit=k,
        with_payload=PAYLOAD,
    )
    return [to_hit(p) for p in result.points]


def bm25_description(query: str, k: int = 10) -> list[Hit]:
    """The k tools whose description text best matches the query's words, best first."""
    from qdrant_client import models

    result = client().query_points(
        collection(),
        query=models.Document(text=query, model="qdrant/bm25"),
        using="bm25",
        query_filter=kind_filter("description"),
        limit=k,
        with_payload=PAYLOAD,
    )
    return [to_hit(p) for p in result.points]


def bm25_names(query: str, k: int = 10) -> list[Hit]:
    """The k tools whose name or labels best match the query's words, best first."""
    from qdrant_client import models

    result = client().query_points(
        names_collection(),
        query=models.Document(text=query, model="qdrant/bm25", options=_name_bm25_options()),
        using="bm25",
        limit=k,
        with_payload=PAYLOAD,
    )
    return [to_hit(p) for p in result.points]


def dense_queries(query: str, k: int = 10) -> list[Hit]:
    """The k tools with the synthetic query closest to this one; a tool scores as its best query."""
    result = client().query_points_groups(
        collection(),
        query=list(encode(query)),
        using="dense",
        query_filter=kind_filter("synthetic_query"),
        group_by="tool_id",
        group_size=1,
        limit=k,
        with_payload=PAYLOAD,
    )
    return [to_hit(g.hits[0]) for g in result.groups]


NEAR_MATCH = 0.9  # SequenceMatcher ratio of the normalised strings
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalise(s: str) -> str:
    """Lowercase ASCII letters and digits only: "Purge_Dups", "purge dups" -> "purgedups"."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return _NON_ALNUM.sub("", s.lower())


def name_match(query: str, hit: Hit, near: float = NEAR_MATCH) -> str | None:
    """
    "exact" if one of the hit's names or labels (newline-separated in its text)
    normalises to the query, "near" if one is within `near` similarity of it ("bwa mem"
    vs "BWA-MEM2"), else None. Short strings must match exactly.
    """
    q = normalise(query)
    if not q:
        return None
    best = None
    for name in hit.text.split("\n"):
        n = normalise(name)
        if n == q:
            return "exact"
        if min(len(n), len(q)) >= 5 and SequenceMatcher(None, n, q).ratio() >= near:
            best = "near"
    return best

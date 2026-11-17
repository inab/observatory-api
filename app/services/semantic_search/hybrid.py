"""Hybrid retrieval: the four retrievers fused with Reciprocal Rank Fusion.

Ported from search-eval `retrieval/hybrid.py` (fusion code unchanged). A tool's score is

    sum over retrievers r of  weight_r(tool) / (rrf_k + rank_r)

RRF uses ranks only, so cosine and BM25 scores never meet. Hits of the names retriever
whose name *is* the query (exactly, or nearly when nothing matches exactly) are weighted
`name_boost`; when no name hit matches, the names retriever is dropped (`names_unmatched`
= 0), since it then only adds tools sharing an ordinary word with the query.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from app.services.semantic_search import retrievers
from app.services.semantic_search.index import Hit, encode

logger = logging.getLogger(__name__)

# (query, k, conditions) -> hits; conditions are {payload field: accepted values}.
RETRIEVERS: dict[str, Callable[[str, int, dict | None], list[Hit]]] = {
    "dense_description": retrievers.dense_description,
    "bm25_description": retrievers.bm25_description,
    "bm25_names": retrievers.bm25_names,
    "dense_queries": retrievers.dense_queries,
}
RRF_K = 60
DEPTH = 100
NAMES = "bm25_names"
NAME_BOOST = 3.0
NAMES_UNMATCHED = 0.0

_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="semantic-search")


class SearchUnavailable(RuntimeError):
    """Every retriever failed (Qdrant down, model not loadable)."""


@dataclass(frozen=True)
class FusedHit:
    tool_id: str
    name: str
    score: float
    ranks: dict[str, int]  # rank in each retriever that returned the tool


def fuse(rankings: dict[str, list[Hit]], k: int = 10, rrf_k: float = RRF_K,
         weights: dict[str, float] | None = None,
         hit_weights: dict[str, dict[str, float]] | None = None) -> list[FusedHit]:
    """The k best tools of several rankings (retriever -> hits, best first)."""
    weights, hit_weights = weights or {}, hit_weights or {}
    scores: dict[str, float] = {}
    ranks: dict[str, dict[str, int]] = {}
    names: dict[str, str] = {}
    for retriever, hits in rankings.items():
        w = weights.get(retriever, 1.0)
        own = hit_weights.get(retriever, {})
        for rank, h in enumerate(hits, 1):
            scores[h.tool_id] = scores.get(h.tool_id, 0.0) + own.get(h.tool_id, w) / (rrf_k + rank)
            ranks.setdefault(h.tool_id, {})[retriever] = rank
            names.setdefault(h.tool_id, h.name)
    # Ties broken by tool id, to be deterministic.
    order = sorted(scores, key=lambda t: (-scores[t], t))[:k]
    return [FusedHit(t, names[t], scores[t], ranks[t]) for t in order]


def name_boosts(query: str, rankings: dict[str, list[Hit]],
                weights: dict[str, float] | None = None,
                name_boost: float = NAME_BOOST) -> dict[str, dict[str, float]]:
    """`hit_weights` for `fuse`: `name_boost` for each exact (else near) name match."""
    w = max((weights or {}).get(NAMES, 1.0), name_boost)
    matches = {h.tool_id: retrievers.name_match(query, h) for h in rankings.get(NAMES, [])}
    level = "exact" if "exact" in matches.values() else "near"
    boosted = {t: w for t, m in matches.items() if m == level}
    return {NAMES: boosted} if boosted else {}


def name_weights(query: str, rankings: dict[str, list[Hit]],
                 weights: dict[str, float] | None = None, name_boost: float = NAME_BOOST,
                 names_unmatched: float = NAMES_UNMATCHED
                 ) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """(`weights`, `hit_weights`) for `fuse`: name matches boosted, names dropped if none."""
    boosts = name_boosts(query, rankings, weights, name_boost)
    weights = dict(weights or {})
    if not boosts:
        weights[NAMES] = names_unmatched
    return weights, boosts


def run(query: str, depth: int = DEPTH,
        conditions: dict[str, list[str]] | None = None) -> dict[str, list[Hit]]:
    """
    Each retriever's top `depth` tools that meet `conditions`, queried concurrently. A failing retriever is
    logged and left out; if all fail, raises SearchUnavailable.
    """
    try:
        encode(query)  # once, before the two dense retrievers race to do it
    except Exception:
        logger.exception("semantic search: query encoding failed; dense retrievers will be skipped")
    futures = {name: _pool.submit(fn, query, depth, conditions) for name, fn in RETRIEVERS.items()}
    rankings, errors = {}, {}
    for name, f in futures.items():
        try:
            rankings[name] = f.result()
        except Exception as err:
            logger.warning("semantic search: retriever %s failed: %s", name, err)
            errors[name] = err
    if not rankings:
        raise SearchUnavailable(
            "semantic search index unavailable: "
            + "; ".join(f"{n}: {e}" for n, e in errors.items()))
    return rankings


def search(query: str, k: int = 10, depth: int = DEPTH,
           conditions: dict[str, list[str]] | None = None) -> list[FusedHit]:
    """The k best tools of the fused retrievers, among those that meet `conditions`."""
    rankings = run(query, depth, conditions)
    return fuse(rankings, k, RRF_K, *name_weights(query, rankings))

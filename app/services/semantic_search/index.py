"""What the retrievers share: the Qdrant client, the query encoder and the shape of a hit.

Ported from search-eval `retrieval/index.py`. The index is built by the pipeline
(`rsetl search-index` in research-software-etl); the API only reads it.

Settings come from environment variables first, then a `[QDRANT]` section of the
`CONFIG_PATH` ini file (same keys), then the defaults below.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from functools import cache, lru_cache

from app.helpers.database import _load_config

logger = logging.getLogger(__name__)

MODEL = "Alibaba-NLP/gte-modernbert-base"  # the model the index was embedded with
MAX_SEQ_LENGTH = 512


_config = cache(_load_config)  # the ini file is read once


def setting(key: str, default: str | None = None) -> str | None:
    val = os.getenv(key)
    if val is not None:
        return val
    config = _config()
    if config.has_option('QDRANT', key):
        return config.get('QDRANT', key)
    return default


def enabled() -> bool:
    """SEMANTIC_SEARCH=0 switches the endpoint off (no model, no Qdrant): CI, dev without Qdrant."""
    return setting('SEMANTIC_SEARCH', '1') != '0'


def collection() -> str:
    return setting('QDRANT_COLLECTION', 'tool_search')


def names_collection() -> str:
    # Experimental, BM25-only, one point per tool (`rsetl search-index --names`).
    return setting('QDRANT_NAMES_COLLECTION', 'tool_search_exp_names')


@dataclass(frozen=True)
class Hit:
    tool_id: str
    name: str
    score: float
    kind: str
    text: str


@cache
def client():
    from qdrant_client import QdrantClient

    return QdrantClient(
        # Always pass url: with an API key and no url the client defaults to https,
        # which fails against a plain-http Qdrant (e.g. an SSH tunnel).
        url=setting('QDRANT_URL', 'http://localhost:6333'),
        api_key=setting('QDRANT_API_KEY'),
        cloud_inference=True,  # BM25 queries are sent as text; Qdrant tokenises them
        timeout=int(setting('QDRANT_TIMEOUT', '30')),
    )


_encoder_lock = threading.Lock()
_encoder = None


def encoder():
    """The sentence-transformers model, loaded once (thread-safe)."""
    global _encoder
    if _encoder is None:
        with _encoder_lock:
            if _encoder is None:
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(MODEL, device='cpu')
                model.max_seq_length = MAX_SEQ_LENGTH  # as the index was built
                _encoder = model
    return _encoder


def warm_up_safe() -> None:
    """Load the model and encode once, so the first request isn't slow. Never raises."""
    try:
        encode("warm up")
        logger.info("semantic search: encoder loaded")
    except Exception:
        logger.exception("semantic search: encoder warm-up failed (will retry on first request)")


@lru_cache(maxsize=4096)
def encode(query: str) -> tuple[float, ...]:
    """As the index was built: no prefix, L2-normalised. Cached (a tuple, so immutable)."""
    return tuple(encoder().encode(query, normalize_embeddings=True).tolist())


# Payload fields the pipeline indexes for filtering (its FILTER_FIELDS), keyed by the
# MongoDB path `_build_filters` uses for them. EDAM term fields hold `term_key`s.
FILTER_PAYLOAD = {
    'data.source': 'sources',
    'data.type': 'type',
    'data.topics.term': 'topics',
    'data.operations.term': 'operations',
    'data.input.term': 'input',
    'data.output.term': 'output',
    'data.license.name': 'license',
    'data.tags': 'tags',
}
TERM_FIELDS = {'topics', 'operations', 'input', 'output'}


def term_key(term: str) -> str:
    """
    An EDAM term as the index stores it: trimmed, leading quote dropped, lowercased.
    MUST match the pipeline's `term_key` (research-software-etl
    src/application/services/semantic_search/search_index.py).
    """
    return term.strip().lstrip('"').strip().lower()


def payload_conditions(filters: dict) -> dict[str, list[str]]:
    """
    `_build_filters` output -> {payload field: accepted values}. Term values are
    normalised with `term_key`, so Qdrant is never stricter than Mongo (its collation is
    case-insensitive); Mongo re-checks every candidate, so results match /search.
    """
    conditions = {}
    for path, cond in filters.items():
        key = FILTER_PAYLOAD.get(path)
        values = cond.get('$in') if isinstance(cond, dict) else None
        if key is None or not values:
            continue
        if key in TERM_FIELDS:
            values = [term_key(v) for v in values]
        conditions[key] = sorted({v for v in values if v})
    return conditions


SCHEMA_TTL = 300  # seconds; a reindex that adds a payload index is picked up within it
_schema_lock = threading.Lock()
_schemas: dict[str, tuple[float, frozenset[str]]] = {}
_warned: dict[str, set[str]] = {}


def indexed_fields(name: str) -> frozenset[str]:
    """The payload fields `name` has an index on (cached for SCHEMA_TTL)."""
    now = time.monotonic()
    with _schema_lock:
        cached = _schemas.get(name)
        if cached and now - cached[0] < SCHEMA_TTL:
            return cached[1]
    fields = frozenset(client().get_collection(name).payload_schema or {})
    with _schema_lock:
        _schemas[name] = (now, fields)
    return fields


def search_filter(name: str, kind: str | None = None,
                  conditions: dict[str, list[str]] | None = None):
    """
    The Qdrant filter for a query on collection `name`: its `kind`, AND each condition
    (any of its values). A condition on a field the collection has no index for (an
    index built before the field existed) is skipped: Mongo still applies it, as before.
    """
    from qdrant_client import models

    must = []
    if kind:
        must.append(models.FieldCondition(key="kind", match=models.MatchValue(value=kind)))
    if conditions:
        indexed = indexed_fields(name)
        skipped = sorted(set(conditions) - indexed - _warned.get(name, set()))
        if skipped:  # once per collection and field, not on every request
            _warned.setdefault(name, set()).update(skipped)
            logger.warning("semantic search: %s has no payload index on %s; "
                           "filtering those after ranking (rerun `rsetl search-index`)",
                           name, ", ".join(skipped))
        must.extend(
            models.FieldCondition(key=key, match=models.MatchAny(any=values))
            for key, values in conditions.items() if key in indexed
        )
    return models.Filter(must=must) if must else None


def to_hit(point) -> Hit:
    p = point.payload
    return Hit(p["tool_id"], p["name"], point.score, p["kind"], p["text"])

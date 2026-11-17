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


def kind_filter(kind: str):
    from qdrant_client import models

    return models.Filter(must=[models.FieldCondition(
        key="kind", match=models.MatchValue(value=kind))])


def to_hit(point) -> Hit:
    p = point.payload
    return Hit(p["tool_id"], p["name"], point.score, p["kind"], p["text"])

"""MongoDB index definitions and the routine that (re)creates them.

The tools collection is rebuilt by the external import pipeline (the old collection is
renamed to `<tools>_archive_<timestamp>` and a fresh one takes its place), and a fresh
collection starts with no indexes. Losing `tools_text_search` breaks `/search` outright
(`OperationFailure: text index required for $text query`); losing the filter indexes
silently turns every filtered search into a collection scan. So indexes are ensured on
API startup (see the lifespan in main.py) as well as on demand, either via
`scripts/create_indexes.py` or by the import pipeline calling POST /admin/reindex
(app/routes/admin.py) right after it swaps in the new collection.
"""
import logging

from pymongo import TEXT, ASCENDING, DESCENDING
from pymongo.collation import Collation
from pymongo.errors import OperationFailure, PyMongoError

from app.helpers.database import connect_DB

logger = logging.getLogger(__name__)

# Case-insensitive collation for the topic/operation term filters. Must match
# TERM_COLLATION in app/routes/search.py so the queries actually use these indexes.
TERM_COLLATION = Collation(locale="en", strength=2)

TEXT_INDEX_NAME = "tools_text_search"

# Indexes on the tools collection, as (keys, kwargs) pairs. Filter fields are used by the
# /search and /initial-search $match; tool_name backs the GET /tool?name=... lookup.
TOOLS_INDEXES = [
    ([("data.source", ASCENDING)], {"name": "filter_source"}),
    ([("data.type", ASCENDING)], {"name": "filter_type"}),
    # /search and /initial-search filter topics/operations by *term* (not uri), matched
    # case-insensitively. The collation makes exact-equality `$in` matches index-backed.
    ([("data.topics.term", ASCENDING)],
     {"name": "filter_topics_term", "collation": TERM_COLLATION}),
    ([("data.operations.term", ASCENDING)],
     {"name": "filter_operations_term", "collation": TERM_COLLATION}),
    ([("data.license.name", ASCENDING)], {"name": "filter_license"}),
    ([("data.tags", ASCENDING)], {"name": "filter_tags"}),
    ([("data.input.term", ASCENDING)], {"name": "filter_input_term"}),
    ([("data.output.term", ASCENDING)], {"name": "filter_output_term"}),
    ([("data.name", ASCENDING)], {"name": "tool_name"}),
]

# Full-text search index backing the $text branch of /search.
TEXT_INDEX_KEYS = [
    ("data.name", TEXT),
    ("data.label", TEXT),
    ("data.description", TEXT),
    ("data.topics.term", TEXT),
    ("data.operations.term", TEXT),
]
TEXT_INDEX_WEIGHTS = {
    "data.name": 10,
    # data.label is a list of alternate names; weight it like the primary name.
    "data.label": 10,
    "data.topics.term": 5,
    "data.operations.term": 5,
    "data.description": 3,
}

STATS_INDEXES = [
    # make_query (all stats endpoints): variable + collection → latest version
    ([("variable", ASCENDING), ("collection", ASCENDING), ("version", DESCENDING)],
     {"name": "stats_lookup"}),
    # hydrate_fairsoft: createdFrom $in filtered by variable
    ([("variable", ASCENDING), ("createdFrom", ASCENDING)], {"name": "stats_fairsoft"}),
]

# Index names from earlier versions: the topic/operation filters now match on .term
# (case-insensitive), not .uri.
STALE_TOOLS_INDEXES = ("filter_topics_uri", "filter_operations_uri")


def ensure_indexes(force_text: bool = False):
    """Create any missing index on the tools and stats collections.

    `create_index` is a no-op when an identical index already exists, so this is cheap to
    call on every startup. The text index is the exception: its fields/weights can't be
    redefined in place (create_index then raises IndexOptionsConflict), so changing them
    requires a drop first. That drop is only done with force_text=True — from the CLI
    script or POST /admin/reindex — because dropping and rebuilding on every API boot
    would leave a window where /search returns IndexNotFound.

    Returns a report of what happened, so callers (the CLI script, the admin endpoint) can
    log a real confirmation instead of a blind success:

        {"tools": {"collection": str, "indexes": [...], "created": [...], "dropped": [...]},
         "stats": {"collection": str, "indexes": [...], "created": [...]},
         "text_index_rebuilt": bool}

    `created` is a before/after diff of the index names. A text index that was dropped and
    rebuilt under force_text is present in both snapshots, so it never shows up there —
    hence the separate text_index_rebuilt flag.
    """
    tools, stats, _, _ = connect_DB()
    try:
        tools_before = {i["name"] for i in tools.list_indexes()}
        stats_before = {i["name"] for i in stats.list_indexes()}
        dropped = []
        text_index_rebuilt = False

        for stale in STALE_TOOLS_INDEXES:
            try:
                tools.drop_index(stale)
                dropped.append(stale)
                logger.info("dropped stale index: %s", stale)
            except OperationFailure:
                pass  # already absent

        for keys, kwargs in TOOLS_INDEXES:
            tools.create_index(keys, **kwargs)

        if force_text:
            try:
                tools.drop_index(TEXT_INDEX_NAME)
                text_index_rebuilt = True
                logger.info("dropped existing index: %s (will recreate)", TEXT_INDEX_NAME)
            except OperationFailure:
                pass  # not present yet
        tools.create_index(
            TEXT_INDEX_KEYS, weights=TEXT_INDEX_WEIGHTS, name=TEXT_INDEX_NAME
        )

        for keys, kwargs in STATS_INDEXES:
            stats.create_index(keys, **kwargs)

        tools_names = [i["name"] for i in tools.list_indexes()]
        stats_names = [i["name"] for i in stats.list_indexes()]
        logger.info("%s indexes: %s", tools.name, tools_names)
        logger.info("%s indexes: %s", stats.name, stats_names)
        return {
            "tools": {
                "collection": tools.name,
                "indexes": tools_names,
                "created": [n for n in tools_names if n not in tools_before],
                "dropped": dropped,
            },
            "stats": {
                "collection": stats.name,
                "indexes": stats_names,
                "created": [n for n in stats_names if n not in stats_before],
            },
            "text_index_rebuilt": text_index_rebuilt,
        }
    finally:
        tools.database.client.close()


def ensure_indexes_safe():
    """ensure_indexes() for the startup path: never raise, just log.

    A DB hiccup or a user without index-creation rights must not stop the API from
    booting — the endpoints degrade (slow scans, failing $text) but everything else
    keeps serving, and the CLI script remains available to fix it.
    """
    try:
        ensure_indexes()
    except PyMongoError:
        logger.exception(
            "Could not ensure MongoDB indexes at startup; /search may fail with "
            "'text index required for $text query'. Run scripts/create_indexes.py."
        )
    except Exception:
        logger.exception("Unexpected error while ensuring MongoDB indexes at startup.")

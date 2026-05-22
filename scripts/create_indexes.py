"""
Run once per environment to create all MongoDB indexes.

Usage:
    CONFIG_PATH=./api-variables/config_db.ini python scripts/create_indexes.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.helpers.database import connect_DB
from pymongo import TEXT, ASCENDING, DESCENDING


def create_indexes():
    tools, stats, pubs, _ = connect_DB()

    # ── toolsDev ──────────────────────────────────────────────────────────────

    # Filter fields (used by /search and /initial-search $match)
    tools.create_index([("data.source", ASCENDING)], name="filter_source")
    tools.create_index([("data.type", ASCENDING)], name="filter_type")
    tools.create_index([("data.topics.uri", ASCENDING)], name="filter_topics_uri")
    tools.create_index([("data.operations.uri", ASCENDING)], name="filter_operations_uri")
    tools.create_index([("data.license.name", ASCENDING)], name="filter_license")
    tools.create_index([("data.tags", ASCENDING)], name="filter_tags")
    tools.create_index([("data.input.term", ASCENDING)], name="filter_input_term")
    tools.create_index([("data.output.term", ASCENDING)], name="filter_output_term")

    # Tool detail lookup (GET /tool?name=...)
    tools.create_index([("data.name", ASCENDING)], name="tool_name")

    # Full-text search (replaces 4-query regex approach in /search)
    tools.create_index(
        [
            ("data.name", TEXT),
            ("data.description", TEXT),
            ("data.topics.term", TEXT),
            ("data.operations.term", TEXT),
        ],
        weights={
            "data.name": 10,
            "data.topics.term": 5,
            "data.operations.term": 5,
            "data.description": 3,
        },
        name="tools_text_search",
    )

    print(f"toolsDev indexes: {[i['name'] for i in tools.list_indexes()]}")

    # ── computationsDev ───────────────────────────────────────────────────────

    # make_query (all stats endpoints): variable + collection → latest version
    stats.create_index(
        [("variable", ASCENDING), ("collection", ASCENDING), ("version", DESCENDING)],
        name="stats_lookup",
    )

    # _hydrate_fairsoft: createdFrom $in filtered by variable
    stats.create_index(
        [("variable", ASCENDING), ("createdFrom", ASCENDING)],
        name="stats_fairsoft",
    )

    print(f"computationsDev indexes: {[i['name'] for i in stats.list_indexes()]}")
    print("Done.")


if __name__ == "__main__":
    create_indexes()

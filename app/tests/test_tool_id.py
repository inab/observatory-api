"""Unit tests for the source+name pattern builder in app/routes/tool.py.

Exercises the pure regex-building helper behind GET /tool/id; needs no MongoDB.
"""
import re

from app.routes.tool import _source_name_pattern


def test_pattern_matches_exact_source_and_name():
    pat = _source_name_pattern("biotools", "lca1")
    assert re.search(pat, "biotools/lca1/undefined/None")
    assert re.search(pat, "biotools/lca1/cmd/1.0.1")


def test_pattern_is_anchored_to_start():
    pat = _source_name_pattern("biotools", "lca1")
    # Same name under a different source must not match.
    assert not re.search(pat, "galaxy/lca1/cmd/1.0.1")


def test_pattern_requires_exact_name_not_prefix():
    pat = _source_name_pattern("biotools", "lca1")
    # "lca1" must not collide with "lca10" thanks to the trailing slash.
    assert not re.search(pat, "biotools/lca10/cmd/1.0.1")


def test_pattern_escapes_metacharacters():
    pat = _source_name_pattern("biotools", "c++.tool")
    assert re.search(pat, "biotools/c++.tool/cmd/1.0")
    # The '.' is literal, not a wildcard.
    assert not re.search(pat, "biotools/cXXXtool/cmd/1.0")

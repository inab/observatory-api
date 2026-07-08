"""Unit tests for the ?searchIn helpers in app/routes/search.py.

These exercise the pure parsing/match-building functions and need no MongoDB.
"""
import pytest
from fastapi import HTTPException

from app.routes.search import _parse_search_in, _build_search_in_match


def test_parse_subset_returns_ordered_aliases():
    assert _parse_search_in("name,description") == ["name", "description"]


def test_parse_all_four_collapses_to_text_path():
    # Selecting every field == default; None tells the caller to use $text.
    assert _parse_search_in("name,description,topics,operations") is None


def test_parse_omitted_or_blank_is_none():
    assert _parse_search_in(None) is None
    assert _parse_search_in("") is None
    assert _parse_search_in(",") is None
    assert _parse_search_in("   ") is None


def test_parse_normalizes_case_whitespace_and_dedupes():
    assert _parse_search_in(" Name , name ,DESCRIPTION") == ["name", "description"]


def test_parse_unknown_alias_raises_400():
    with pytest.raises(HTTPException) as exc:
        _parse_search_in("foo")
    assert exc.value.status_code == 400
    assert "foo" in exc.value.detail


def test_build_match_escapes_metachars_and_searches_name_and_label():
    # `name` expands to both data.name and data.label.
    match = _build_search_in_match("c++", ["name"])
    assert match == {"$or": [
        {"data.name": {"$regex": r"c\+\+", "$options": "i"}},
        {"data.label": {"$regex": r"c\+\+", "$options": "i"}},
    ]}


def test_build_match_ors_each_field_by_each_word():
    match = _build_search_in_match("multiple alignment", ["name", "description"])
    assert match["$or"] == [
        {"data.name": {"$regex": "multiple", "$options": "i"}},
        {"data.name": {"$regex": "alignment", "$options": "i"}},
        {"data.label": {"$regex": "multiple", "$options": "i"}},
        {"data.label": {"$regex": "alignment", "$options": "i"}},
        {"data.description": {"$regex": "multiple", "$options": "i"}},
        {"data.description": {"$regex": "alignment", "$options": "i"}},
    ]


def test_build_match_empty_query_returns_empty():
    assert _build_search_in_match("   ", ["name"]) == {}

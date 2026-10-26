"""Unit tests for the JSON-LD and CFF metadata builders.

Exercises app/helpers/makejson.py and app/helpers/makecff.py directly; needs no MongoDB.
"""
from app.helpers import makecff
from app.helpers.makejson import build_json_ld, get_keywords, get_single_author


def test_jsonld_exports_webpage_as_url():
    meta = build_json_ld({"name": "protk", "webpage": ["https://example.org"]})
    assert meta["schema:url"] == ["https://example.org"]


def test_jsonld_exports_registration_not_mandatory():
    meta = build_json_ld({"name": "protk", "registration_not_mandatory": True})
    assert meta["schema:isAccessibleForFree"] is True


def test_organisation_author_keeps_name():
    author = get_single_author({"type": "organization", "name": "BSC"})
    assert author == {"@type": "schema:Organization", "schema:name": "BSC"}


def test_keywords_topic_without_uri_uses_term():
    topics = [
        {"vocabulary": "EDAM", "uri": "http://edamontology.org/topic_0121", "term": "Proteomics"},
        {"term": "Plain topic"},
        {"vocabulary": "EDAM", "term": "EDAM without URI"},
    ]
    assert get_keywords(topics) == ["edam:topic_0121", "Plain topic", "EDAM without URI"]


def test_identifier_unwraps_version_list():
    meta = build_json_ld({"name": "protk", "version": ["1.4.4a"], "type": ["cmd"]})
    assert meta["@id"].endswith("observatory:protk:1.4.4a/cmd")


def test_cff_without_license(monkeypatch):
    # Must not reach the license-mapping service, nor fail when no license is given
    monkeypatch.setattr(makecff, "map_license", lambda name: None)
    cff = makecff.create_cff({"name": "protk", "authors": [{"name": "Jane"}], "license": []})
    assert "title: protk" in cff
    assert "license" not in cff

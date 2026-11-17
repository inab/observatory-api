"""Tests for the semantic search: the fusion rules (pure) and GET /semantic-search.

No Qdrant, no model, no MongoDB: the endpoint tests monkeypatch `hybrid.search` and the
collections. The fusion tests pin the behaviour evaluated in search-eval.
"""
import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes import semantic_search
from app.services.semantic_search import hybrid
from app.services.semantic_search.hybrid import FusedHit, fuse, name_boosts, name_weights
from app.services.semantic_search.index import Hit
from app.services.semantic_search.retrievers import name_match, normalise


def hit(tool_id, name=None, text=None):
    name = name or tool_id
    return Hit(tool_id, name, 1.0, "x", text if text is not None else name)


# --- name matching -------------------------------------------------------------------

def test_normalise_ignores_case_punctuation_and_spaces():
    assert normalise("Purge_Dups") == normalise("purge dups") == "purgedups"


def test_name_match_exact_on_any_label():
    assert name_match("purge dups", hit("t", text="purge_dups\nPurge-Dups tool")) == "exact"


def test_name_match_near_for_a_version_suffix():
    assert name_match("bwa mem", hit("t", text="BWA-MEM2")) == "near"


def test_name_match_short_names_must_match_exactly():
    assert name_match("STAR", hit("t", text="STARS")) is None
    assert name_match("star", hit("t", text="STAR")) == "exact"


def test_name_match_blank_query():
    assert name_match("  --  ", hit("t")) is None


# --- fusion --------------------------------------------------------------------------

def test_fuse_rrf_sums_over_retrievers_and_breaks_ties_by_id():
    rankings = {"a": [hit("x"), hit("y")], "b": [hit("y"), hit("x")], "c": [hit("z")]}
    fused = fuse(rankings, k=3)
    # x and y tie (1/61 + 1/62 each) and z has 1/61: order by score, then id.
    assert [h.tool_id for h in fused] == ["x", "y", "z"]
    assert fused[0].ranks == {"a": 1, "b": 2}


def test_exact_name_match_boosted_and_near_matches_not():
    rankings = {hybrid.NAMES: [hit("mem2", text="BWA-MEM2"), hit("mem", text="bwa_mem")]}
    assert name_boosts("bwa mem", rankings) == {hybrid.NAMES: {"mem": hybrid.NAME_BOOST}}


def test_near_matches_boosted_when_none_exact():
    rankings = {hybrid.NAMES: [hit("mem2", text="BWA-MEM2"), hit("other", text="minimap2")]}
    assert name_boosts("bwa mem", rankings) == {hybrid.NAMES: {"mem2": hybrid.NAME_BOOST}}


def test_names_retriever_dropped_without_a_name_match():
    rankings = {
        "dense_description": [hit("purge")],
        hybrid.NAMES: [hit("diploid", text="Diploid Constructor")],
    }
    weights, boosts = name_weights("remove haplotigs from a diploid assembly", rankings)
    assert boosts == {} and weights[hybrid.NAMES] == 0.0
    fused = fuse(rankings, 10, hybrid.RRF_K, weights, boosts)
    assert fused[0].tool_id == "purge"
    assert dict((h.tool_id, h.score) for h in fused)["diploid"] == 0.0


def test_name_lookup_outvotes_other_retrievers():
    # samtools is only 7th elsewhere; the boosted name hit lifts it over the tool *about* it.
    others = [hit("about_samtools")] + [hit(f"filler{n}") for n in range(5)] + [hit("samtools")]
    rankings = {"dense_description": others, "bm25_description": others, "dense_queries": others,
                hybrid.NAMES: [hit("samtools", text="samtools")]}
    fused = fuse(rankings, 10, hybrid.RRF_K, *name_weights("samtools", rankings))
    assert fused[0].tool_id == "samtools"


def test_run_skips_a_failing_retriever(monkeypatch):
    def boom(q, k):
        raise ConnectionError("down")

    monkeypatch.setattr(hybrid, "encode", lambda q: ())
    monkeypatch.setattr(hybrid, "RETRIEVERS", {"ok": lambda q, k: [hit("a")], "bad": boom})
    assert list(hybrid.run("q")) == ["ok"]


def test_run_raises_when_every_retriever_fails(monkeypatch):
    def boom(q, k):
        raise ConnectionError("down")

    monkeypatch.setattr(hybrid, "encode", lambda q: ())
    monkeypatch.setattr(hybrid, "RETRIEVERS", {"bad": boom})
    with pytest.raises(hybrid.SearchUnavailable):
        hybrid.run("q")


# --- endpoint ------------------------------------------------------------------------

IDS = [str(ObjectId()) for _ in range(25)]
# Every third tool is a "web" tool, the rest "cmd".
DOCS = {i: {"_id": ObjectId(i), "data": {"name": f"tool{n}", "type": ["web" if n % 3 == 0 else "cmd"]}}
        for n, i in enumerate(IDS)}


class FakeTools:
    """Just enough of a pymongo collection: `_id: {$in}` and `data.type: {$in}`."""

    def find(self, match, projection=None, collation=None):
        ids = {str(o) for o in match["_id"]["$in"]}
        types = set(match.get("data.type", {}).get("$in", [])) or None
        for i, doc in DOCS.items():
            if i in ids and (types is None or types & set(doc["data"]["type"])):
                yield {"_id": doc["_id"], "data": dict(doc["data"])}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("SEMANTIC_SEARCH", raising=False)
    # The hybrid's order is IDS reversed, so ordering by _id would be visibly wrong.
    ranked = [FusedHit(i, DOCS[i]["data"]["name"], 1.0 / (n + 1), {"dense_queries": n + 1})
              for n, i in enumerate(reversed(IDS))]
    monkeypatch.setattr(semantic_search.hybrid, "search", lambda q, k: ranked[:k])
    monkeypatch.setattr(semantic_search, "_collections", lambda: (FakeTools(), None, None))
    monkeypatch.setattr(semantic_search, "_finalize_tools", lambda tools, pubs, stats: tools)
    app = FastAPI()
    app.include_router(semantic_search.router)
    return TestClient(app)


def test_keeps_hybrid_order_and_paginates(client):
    body = client.get("/semantic-search", params={"q": "align reads"}).json()
    assert body["total_tools"] == 25
    assert [t["id"] for t in body["tools"]] == list(reversed(IDS))[:10]
    assert body["tools"][0]["ranks"] == {"dense_queries": 1}
    assert body["tools"][0]["semantic_score"] == 1.0
    last = client.get("/semantic-search", params={"q": "align reads", "page": 2}).json()
    assert [t["id"] for t in last["tools"]] == list(reversed(IDS))[20:]


def test_filters_apply_after_ranking(client):
    body = client.get("/semantic-search", params={"q": "align reads", "type": "web"}).json()
    expected = [i for i in reversed(IDS) if DOCS[i]["data"]["type"] == ["web"]]
    assert body["total_tools"] == len(expected) == 9
    assert [t["id"] for t in body["tools"]] == expected[:10]
    assert body["stats"]["type"] == {"web": 9}


def test_candidates_cap_results(client, monkeypatch):
    monkeypatch.setenv("SEMANTIC_SEARCH_CANDIDATES", "5")
    assert client.get("/semantic-search", params={"q": "x"}).json()["total_tools"] == 5


def test_blank_or_missing_query_rejected(client):
    assert client.get("/semantic-search", params={"q": "   "}).status_code == 400
    assert client.get("/semantic-search").status_code == 422


def test_disabled_returns_503(client, monkeypatch):
    monkeypatch.setenv("SEMANTIC_SEARCH", "0")
    assert client.get("/semantic-search", params={"q": "x"}).status_code == 503


def test_index_unavailable_returns_503(client, monkeypatch):
    def down(q, k):
        raise hybrid.SearchUnavailable("down")

    monkeypatch.setattr(semantic_search.hybrid, "search", down)
    assert client.get("/semantic-search", params={"q": "x"}).status_code == 503

"""Tests for POST /admin/reindex (app/routes/admin.py).

ensure_indexes is monkeypatched throughout: CI runs these with no MongoDB, and a real call
would drop and rebuild indexes on whatever database CONFIG_PATH happens to point at.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo.errors import OperationFailure

from app.routes import admin
from app.helpers.indexes import (
    CollectionNotAllowed,
    CollectionNotFound,
    STATS_INDEXES,
    TEXT_INDEX_NAME,
    TOOLS_INDEXES,
)

TOKEN = "test-admin-token"


def _fake_report():
    """What ensure_indexes returns for a collection that had nothing but _id.

    Built from the real index definitions so the assertions below are about the actual
    index set, not a hand-copied list that can drift.
    """
    tools_names = ["_id_"] + [kwargs["name"] for _, kwargs in TOOLS_INDEXES] + [TEXT_INDEX_NAME]
    stats_names = ["_id_"] + [kwargs["name"] for _, kwargs in STATS_INDEXES]
    return {
        "tools": {
            "collection": "tools",
            "indexes": tools_names,
            "created": tools_names[1:],
            "dropped": [],
        },
        "stats": {
            "collection": "stats",
            "indexes": stats_names,
            "created": stats_names[1:],
        },
        "text_index_rebuilt": False,
    }


@pytest.fixture
def calls(monkeypatch):
    """Record every ensure_indexes call instead of touching MongoDB."""
    recorded = []

    def fake_ensure_indexes(force_text=False, tools_collection=None):
        recorded.append({"force_text": force_text, "tools_collection": tools_collection})
        return _fake_report()

    monkeypatch.setattr(admin, "ensure_indexes", fake_ensure_indexes)
    return recorded


@pytest.fixture
def client(monkeypatch):
    """A client over just the admin router.

    Not main.app: that would run the lifespan's ensure_indexes_safe() against a real
    database and needs the static/ mount.
    """
    monkeypatch.setenv(admin.ADMIN_TOKEN_ENV, TOKEN)
    app = FastAPI()
    app.include_router(admin.router, prefix="/admin")
    return TestClient(app)


def _auth(token=TOKEN):
    return {"Authorization": f"Bearer {token}"}


def test_missing_token_is_401_and_does_not_touch_the_db(client, calls):
    response = client.post("/admin/reindex")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert calls == []


def test_wrong_token_is_403_and_does_not_touch_the_db(client, calls):
    response = client.post("/admin/reindex", headers=_auth("not-the-token"))
    assert response.status_code == 403
    assert calls == []


def test_valid_token_reports_the_created_indexes(client, calls):
    response = client.post("/admin/reindex", headers=_auth())
    assert response.status_code == 200

    body = response.json()
    tools_indexes = body["tools"]["indexes"]
    # /search's $text query needs this one; the filters need the rest.
    assert TEXT_INDEX_NAME in tools_indexes
    assert "filter_source" in tools_indexes
    assert "filter_topics_term" in tools_indexes
    assert "tool_name" in tools_indexes
    assert "stats_lookup" in body["stats"]["indexes"]
    assert body["tools"]["created"] == body["tools"]["indexes"][1:]
    assert calls == [{"force_text": False, "tools_collection": None}]


def test_body_is_optional_and_defaults_to_no_text_rebuild(client, calls):
    # The pipeline may POST with no payload at all.
    response = client.post("/admin/reindex", headers=_auth())
    assert response.status_code == 200
    assert response.json()["force_text"] is False
    assert calls == [{"force_text": False, "tools_collection": None}]


def test_force_text_is_passed_through(client, calls):
    response = client.post(
        "/admin/reindex", headers=_auth(), json={"force_text": True}
    )
    assert response.status_code == 200
    assert response.json()["force_text"] is True
    assert calls == [{"force_text": True, "tools_collection": None}]


def test_collection_is_passed_through(client, calls):
    response = client.post(
        "/admin/reindex", headers=_auth(), json={"collection": "toolsDev_next"}
    )
    assert response.status_code == 200
    assert calls == [{"force_text": False, "tools_collection": "toolsDev_next"}]


def test_disallowed_collection_is_400(client, monkeypatch):
    def refuse(force_text=False, tools_collection=None):
        raise CollectionNotAllowed(f"'{tools_collection}' is not an indexable tools collection")

    monkeypatch.setattr(admin, "ensure_indexes", refuse)
    response = client.post(
        "/admin/reindex", headers=_auth(), json={"collection": "toolsDev_archive_x"}
    )
    assert response.status_code == 400
    assert "toolsDev_archive_x" in response.json()["detail"]


def test_missing_collection_is_404(client, monkeypatch):
    def missing(force_text=False, tools_collection=None):
        raise CollectionNotFound(f"collection '{tools_collection}' does not exist")

    monkeypatch.setattr(admin, "ensure_indexes", missing)
    response = client.post(
        "/admin/reindex", headers=_auth(), json={"collection": "toolsDev_next"}
    )
    assert response.status_code == 404
    # A refused request must not leave the endpoint locked.
    assert not admin._reindex_lock.locked()


def test_calling_twice_is_idempotent(client, calls):
    assert client.post("/admin/reindex", headers=_auth()).status_code == 200
    assert client.post("/admin/reindex", headers=_auth()).status_code == 200
    assert len(calls) == 2


def test_unconfigured_token_is_503_not_open_access(client, calls, monkeypatch, tmp_path):
    # Fail closed: with no secret set anywhere, no request gets through — not even one
    # carrying what would otherwise be the right token.
    monkeypatch.delenv(admin.ADMIN_TOKEN_ENV, raising=False)
    monkeypatch.setenv("CONFIG_PATH", str(tmp_path / "does-not-exist.ini"))

    assert client.post("/admin/reindex", headers=_auth()).status_code == 503
    assert client.post("/admin/reindex").status_code == 503
    assert calls == []


def test_token_falls_back_to_the_ini_file(client, calls, monkeypatch, tmp_path):
    monkeypatch.delenv(admin.ADMIN_TOKEN_ENV, raising=False)
    ini = tmp_path / "config_db.ini"
    ini.write_text(f"[ADMIN]\nADMIN_TOKEN = {TOKEN}\n")
    monkeypatch.setenv("CONFIG_PATH", str(ini))

    assert client.post("/admin/reindex", headers=_auth()).status_code == 200
    assert client.post("/admin/reindex", headers=_auth("nope")).status_code == 403
    assert len(calls) == 1


def test_mongo_failure_surfaces_as_500(client, monkeypatch):
    # The on-demand path must not swallow errors the way ensure_indexes_safe does.
    def boom(force_text=False, tools_collection=None):
        raise OperationFailure("not authorized on observatory to execute createIndexes")

    monkeypatch.setattr(admin, "ensure_indexes", boom)

    response = client.post("/admin/reindex", headers=_auth())
    assert response.status_code == 500
    assert "not authorized" in response.json()["detail"]


def test_lock_is_released_after_a_failure(client, calls, monkeypatch):
    # A failed rebuild must not wedge the endpoint at 409 forever.
    def boom(force_text=False, tools_collection=None):
        raise OperationFailure("transient")

    monkeypatch.setattr(admin, "ensure_indexes", boom)
    assert client.post("/admin/reindex", headers=_auth()).status_code == 500

    monkeypatch.setattr(admin, "ensure_indexes", lambda force_text=False, tools_collection=None: _fake_report())
    assert client.post("/admin/reindex", headers=_auth()).status_code == 200


def test_concurrent_rebuild_is_rejected_with_409(client, monkeypatch):
    admin._reindex_lock.acquire()
    try:
        response = client.post("/admin/reindex", headers=_auth())
        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]
    finally:
        admin._reindex_lock.release()

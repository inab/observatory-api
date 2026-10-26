"""Tests for which tools collection ensure_indexes targets (app/helpers/indexes.py).

connect_DB is monkeypatched with in-memory fakes: CI has no MongoDB, and these tests are
about the allowlist and existence check, not about pymongo.
"""
import pytest

from app.helpers import indexes
from app.helpers.indexes import (
    CollectionNotAllowed,
    CollectionNotFound,
    TEXT_INDEX_NAME,
    allowed_tools_collections,
)


class FakeCollection:
    def __init__(self, database, name):
        self.database = database
        self.name = name
        self.index_names = ["_id_"]

    def list_indexes(self):
        return [{"name": n} for n in self.index_names]

    def create_index(self, keys, name, **kwargs):
        if name not in self.index_names:
            self.index_names.append(name)

    def drop_index(self, name):
        from pymongo.errors import OperationFailure

        if name not in self.index_names:
            raise OperationFailure(f"index not found with name [{name}]")
        self.index_names.remove(name)


class FakeClient:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeDatabase:
    def __init__(self, existing):
        self.name = "observatory"
        self.client = FakeClient()
        self.collections = {name: FakeCollection(self, name) for name in existing}

    def __getitem__(self, name):
        # Like pymongo, looking a collection up does not require it to exist.
        return self.collections.setdefault(name, FakeCollection(self, name))

    def list_collection_names(self, filter=None):
        names = list(self.collections)
        if filter and "name" in filter:
            names = [n for n in names if n == filter["name"]]
        return names


@pytest.fixture
def db(monkeypatch):
    database = FakeDatabase(["toolsDev", "toolsDev_next", "toolsDev_archive_x", "stats"])
    monkeypatch.setattr(
        indexes,
        "connect_DB",
        lambda: (database["toolsDev"], database["stats"], None, None),
    )
    return database


def test_allowlist_is_live_and_staging_only():
    assert allowed_tools_collections("toolsDev") == ("toolsDev", "toolsDev_next")


def test_default_indexes_the_configured_collection(db):
    report = indexes.ensure_indexes()
    assert report["tools"]["collection"] == "toolsDev"
    assert TEXT_INDEX_NAME in db.collections["toolsDev"].index_names
    assert db.collections["toolsDev_next"].index_names == ["_id_"]
    assert db.client.closed


def test_naming_the_configured_collection_is_the_default(db):
    report = indexes.ensure_indexes(tools_collection="toolsDev")
    assert report["tools"]["collection"] == "toolsDev"


def test_staging_collection_is_indexed_and_live_is_left_alone(db):
    report = indexes.ensure_indexes(tools_collection="toolsDev_next")
    assert report["tools"]["collection"] == "toolsDev_next"
    assert TEXT_INDEX_NAME in report["tools"]["created"]
    assert TEXT_INDEX_NAME in db.collections["toolsDev_next"].index_names
    assert db.collections["toolsDev"].index_names == ["_id_"]


@pytest.mark.parametrize("name", ["toolsDev_archive_x", "toolsDev_nextx", "stats", "other"])
def test_collection_outside_the_allowlist_is_refused(db, name):
    with pytest.raises(CollectionNotAllowed):
        indexes.ensure_indexes(tools_collection=name)
    # Refused before any index was touched, and the client still closed.
    assert all(c.index_names == ["_id_"] for c in db.collections.values())
    assert db.client.closed


def test_missing_staging_collection_is_not_created(db):
    # create_index would silently create it; the request must fail instead.
    del db.collections["toolsDev_next"]
    with pytest.raises(CollectionNotFound):
        indexes.ensure_indexes(tools_collection="toolsDev_next")
    assert "toolsDev_next" not in db.collections
    assert db.collections["stats"].index_names == ["_id_"]

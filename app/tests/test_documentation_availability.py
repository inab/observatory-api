"""Unit tests for hydrate_documentation_availability in app/helpers/utils.py.

Uses an in-memory fake of the availability collection; needs no MongoDB.
"""
from app.helpers.utils import hydrate_documentation_availability


class FakeAvailabilityCollection:
    """Supports the one query shape used: {'_id': {'$in': [...]}} with a $slice: -1 projection."""

    def __init__(self, docs):
        self.docs = {doc['_id']: doc for doc in docs}
        self.find_calls = 0

    def find(self, filter, projection=None):
        self.find_calls += 1
        for _id in filter['_id']['$in']:
            doc = self.docs.get(_id)
            if doc is None:
                continue
            history = doc.get('data', {}).get('availability', [])
            yield {'_id': _id, 'data': {'availability': history[-1:]}}


def _avail_doc(url, readings):
    return {'_id': url, 'is_relevant': True, 'data': {'url': url, 'availability': readings}}


def _reading(code, date='2026-09-14T09:04:16Z', access_time=2.34):
    return {'date': date, 'code': code, 'access_time': access_time}


def test_monitored_url_returns_latest_reading():
    url = 'https://example.org/docs.html'
    coll = FakeAvailabilityCollection([
        _avail_doc(url, [_reading(404, date='2026-09-13T09:00:00Z'), _reading(200)]),
    ])
    tool = {'documentation': [{'type': 'general', 'url': url}]}

    hydrate_documentation_availability(tool, coll)

    assert tool['documentation'][0]['availability'] == {
        'monitored': True,
        'latest': {'date': '2026-09-14T09:04:16Z', 'code': 200, 'access_time': 2.34},
    }


def test_monitored_but_unreachable_keeps_null_code():
    url = 'https://down.example.org/'
    coll = FakeAvailabilityCollection([_avail_doc(url, [_reading(None, access_time=None)])])
    tool = {'documentation': [{'type': 'manual', 'url': url}]}

    hydrate_documentation_availability(tool, coll)

    availability = tool['documentation'][0]['availability']
    assert availability['monitored'] is True
    assert availability['latest']['code'] is None


def test_monitored_with_empty_history():
    url = 'https://example.org/empty'
    coll = FakeAvailabilityCollection([_avail_doc(url, [])])
    tool = {'documentation': [{'type': 'general', 'url': url}]}

    hydrate_documentation_availability(tool, coll)

    assert tool['documentation'][0]['availability'] == {'monitored': True, 'latest': None}


def test_unmonitored_url():
    coll = FakeAvailabilityCollection([])
    tool = {'documentation': [{'type': 'general', 'url': 'https://example.org/new'}]}

    hydrate_documentation_availability(tool, coll)

    assert tool['documentation'][0]['availability'] == {'monitored': False, 'latest': None}


def test_items_without_http_url_are_untouched():
    coll = FakeAvailabilityCollection([])
    help_item = {'type': 'help', 'url': None, 'content': 'Run with --help'}
    ftp_item = {'type': 'general', 'url': 'ftp://example.org/docs'}
    tool = {'documentation': [help_item, ftp_item, 'plain string']}

    hydrate_documentation_availability(tool, coll)

    assert 'availability' not in help_item
    assert 'availability' not in ftp_item
    assert coll.find_calls == 0


def test_trailing_slash_mismatch_is_matched():
    coll = FakeAvailabilityCollection([
        _avail_doc('https://example.org/docs/', [_reading(200)]),
        _avail_doc('https://example.org/other', [_reading(301)]),
    ])
    tool = {'documentation': [
        {'type': 'general', 'url': 'https://example.org/docs'},
        {'type': 'general', 'url': 'https://example.org/other/'},
    ]}

    hydrate_documentation_availability(tool, coll)

    assert tool['documentation'][0]['availability']['latest']['code'] == 200
    assert tool['documentation'][1]['availability']['latest']['code'] == 301


def test_exact_match_preferred_over_toggled_slash():
    coll = FakeAvailabilityCollection([
        _avail_doc('https://example.org/docs', [_reading(200)]),
        _avail_doc('https://example.org/docs/', [_reading(404)]),
    ])
    tool = {'documentation': [{'type': 'general', 'url': 'https://example.org/docs/'}]}

    hydrate_documentation_availability(tool, coll)

    assert tool['documentation'][0]['availability']['latest']['code'] == 404


def test_no_documentation_makes_no_query():
    coll = FakeAvailabilityCollection([])
    for tool in ({}, {'documentation': None}, {'documentation': []}):
        hydrate_documentation_availability(tool, coll)
    assert coll.find_calls == 0


def test_duplicate_urls_hydrated_with_single_query():
    url = 'https://example.org/docs.html'
    coll = FakeAvailabilityCollection([_avail_doc(url, [_reading(200)])])
    tool = {'documentation': [
        {'type': 'general', 'url': url},
        {'type': 'manual', 'url': url},
    ]}

    hydrate_documentation_availability(tool, coll)

    assert coll.find_calls == 1
    assert all(item['availability']['latest']['code'] == 200 for item in tool['documentation'])

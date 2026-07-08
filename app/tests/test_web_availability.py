"""Unit tests for the date helpers in app/routes/web_availability.py.

These exercise the pure timestamp-parsing/filtering functions and need no MongoDB.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.routes.web_availability import (
    _parse_iso_datetime,
    _build_daily_availability,
)


def _iso(dt: datetime) -> str:
    """Microsecond-precision ISO string with trailing Z, as stored in the DB."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _null_iso(d) -> str:
    """ISO date the API uses for synthetic missing-day slots (midnight UTC, Z)."""
    return d.strftime("%Y-%m-%dT00:00:00Z")


def test_parse_microsecond_precision_with_z():
    dt = _parse_iso_datetime("2024-06-02T02:17:39.932171Z")
    assert dt == datetime(2024, 6, 2, 2, 17, 39, 932171, tzinfo=timezone.utc)


def test_parse_explicit_utc_offset():
    dt = _parse_iso_datetime("2025-11-04T11:58:56.339012+00:00")
    assert dt == datetime(2025, 11, 4, 11, 58, 56, 339012, tzinfo=timezone.utc)


def test_parse_nanosecond_precision_is_truncated_to_microseconds():
    # Regression: 9-digit (nanosecond) fractional seconds used to raise
    # ValueError on Python < 3.11 and were silently dropped, collapsing the
    # 6-month availability window to a handful of points.
    dt = _parse_iso_datetime("2026-06-04T09:11:20.560689149Z")
    assert dt == datetime(2026, 6, 4, 9, 11, 20, 560689, tzinfo=timezone.utc)


def test_parse_no_fractional_seconds():
    dt = _parse_iso_datetime("2026-06-04T09:11:20Z")
    assert dt == datetime(2026, 6, 4, 9, 11, 20, tzinfo=timezone.utc)


def test_parse_naive_datetime_assumed_utc():
    dt = _parse_iso_datetime("2026-06-04T09:11:20.123456")
    assert dt == datetime(2026, 6, 4, 9, 11, 20, 123456, tzinfo=timezone.utc)


def test_parse_empty_string_raises():
    with pytest.raises(ValueError):
        _parse_iso_datetime("")


# --- _build_daily_availability -------------------------------------------

def _dates(series: list[dict]) -> list[str]:
    return [item["date"] for item in series]


def test_daily_series_no_gaps_keeps_real_entries():
    # Three consecutive days, each with a real point, inside a 7-day window.
    now = datetime.now(timezone.utc)
    items = []
    for d in (3, 2, 1):  # out of order on purpose
        dt = now - timedelta(days=d)
        items.append({"date": _iso(dt), "code": 200, "access_time": 100 + d})

    series = _build_daily_availability(items, days=7)

    # Full 7-day grid (today-7 .. today inclusive == 8 calendar days).
    assert len(series) == 8
    # The three real points are present with their original ISO strings.
    real = [s for s in series if s["code"] is not None]
    assert len(real) == 3
    assert {s["access_time"] for s in real} == {101, 102, 103}
    assert all(set(s) == {"date", "code", "access_time"} for s in series)


def test_daily_series_fills_internal_gap_with_null():
    now = datetime.now(timezone.utc)
    d3 = now - timedelta(days=3)
    d1 = now - timedelta(days=1)
    # day-2 is intentionally missing
    items = [
        {"date": _iso(d3), "code": 200, "access_time": 10},
        {"date": _iso(d1), "code": 200, "access_time": 20},
    ]

    series = _build_daily_availability(items, days=7)

    gap_day = _null_iso((now - timedelta(days=2)).date())
    gap = [s for s in series if s["date"] == gap_day]
    assert gap == [{"date": gap_day, "code": None, "access_time": None}]


def test_daily_series_full_window_all_null_when_empty():
    series = _build_daily_availability([], days=7)

    # Exactly 8 contiguous null slots (today-7 .. today inclusive).
    assert len(series) == 8
    assert all(s["code"] is None and s["access_time"] is None for s in series)
    today = datetime.now(timezone.utc).date()
    expected = [_null_iso(today - timedelta(days=n)) for n in range(7, -1, -1)]
    assert _dates(series) == expected


def test_daily_series_keeps_nanosecond_points():
    now = datetime.now(timezone.utc)
    recent = now - timedelta(days=1)
    nano = recent.strftime("%Y-%m-%dT%H:%M:%S.%f") + "149Z"

    series = _build_daily_availability(
        [{"date": nano, "code": 200, "access_time": 12}], days=7
    )

    real = [s for s in series if s["code"] is not None]
    assert len(real) == 1
    assert real[0]["date"] == nano


def test_daily_series_preserves_multiple_points_on_same_day():
    now = datetime.now(timezone.utc)
    base = (now - timedelta(days=2)).replace(hour=1, minute=0, second=0, microsecond=0)
    p_late = base.replace(hour=13)
    p_early = base.replace(hour=1)
    items = [
        {"date": _iso(p_late), "code": 200, "access_time": 99},
        {"date": _iso(p_early), "code": 500, "access_time": 11},
    ]

    series = _build_daily_availability(items, days=7)

    day = base.date().isoformat()
    same_day = [s for s in series if s["date"].startswith(day)]
    # Both real points kept, sorted ascending, no null slot for that day.
    assert [s["access_time"] for s in same_day] == [11, 99]
    assert all(s["code"] is not None for s in same_day)


def test_daily_series_excludes_out_of_window_points():
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=400)
    recent = now - timedelta(days=1)
    items = [
        {"date": _iso(old), "code": 200, "access_time": 1},
        {"date": _iso(recent), "code": 200, "access_time": 2},
    ]

    series = _build_daily_availability(items, days=30)

    real = [s for s in series if s["code"] is not None]
    assert len(real) == 1
    assert real[0]["access_time"] == 2


def test_daily_series_skips_unparseable_date_but_keeps_null_slot(caplog):
    # A point whose date is garbage: it is dropped, but the grid still covers the
    # whole window so every day appears as a null slot.
    items = [{"date": "not-a-date", "code": 200, "access_time": 5}]

    import logging
    with caplog.at_level(logging.WARNING):
        series = _build_daily_availability(items, days=7)

    assert any("unparseable date" in rec.message for rec in caplog.records)
    assert all(s["code"] is None for s in series)
    assert len(series) == 8


def test_daily_series_dates_are_non_decreasing():
    now = datetime.now(timezone.utc)
    items = [
        {"date": _iso(now - timedelta(days=5)), "code": 200},
        {"date": _iso(now - timedelta(days=1)), "code": 200},
    ]
    series = _build_daily_availability(items, days=30)
    parsed = [_parse_iso_datetime(s["date"]) for s in series]
    assert parsed == sorted(parsed)

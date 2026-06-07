import logging
import re
from datetime import datetime, timedelta, timezone
from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel
from app.helpers.database import connect_DB


logger = logging.getLogger(__name__)

router = APIRouter()

tools_collection, stats, pubs_collection, availability_collection = connect_DB()


class URLRequest(BaseModel):
    url: str


# Fractional-seconds component of an ISO timestamp (a dot followed by digits).
_FRACTIONAL_SECONDS_RE = re.compile(r"\.(\d+)")


def _parse_iso_datetime(s: str) -> datetime:
    """
    Parse ISO datetime strings like:
      - 2024-06-02T02:17:39.932171Z
      - 2025-11-04T11:58:56.339012+00:00
      - 2026-06-04T09:11:20.560689149Z  (nanosecond precision)
    Returns a timezone-aware datetime in UTC.
    """
    if not s:
        raise ValueError("Empty date string")

    # Handle trailing 'Z' (Zulu/UTC)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    # datetime.fromisoformat only accepts 3- or 6-digit fractional seconds (on
    # Python < 3.11). Some records are stored with nanosecond (9-digit)
    # precision, so truncate the fractional part to 6 digits (microseconds).
    s = _FRACTIONAL_SECONDS_RE.sub(lambda m: "." + m.group(1)[:6], s)

    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # If somehow stored without tz, assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _get_availability_doc_by_url(web_url: str) -> dict | None:
    """
    Fetch minimal doc needed for availability response.
    For each candidate URL, tries _id == url first, then the url field. If nothing matches,
    retries with the trailing slash toggled (appended when absent, removed when present),
    since stored URLs are inconsistently normalised with/without a trailing '/'.
    """
    candidates = [web_url]
    if web_url.endswith("/"):
        candidates.append(web_url[:-1])
    else:
        candidates.append(web_url + "/")

    for candidate in candidates:
        doc = availability_collection.find_one(
            {"_id": candidate},
            projection={"_id": 0, "url": 1, "data.availability": 1},
        )
        if doc is None:
            doc = availability_collection.find_one(
                {"url": candidate},
                projection={"_id": 0, "url": 1, "data.availability": 1},
            )
        if doc is not None:
            return doc
    return None


def _build_daily_availability(availability: list[dict], days: int) -> list[dict]:
    """
    Build a gap-free daily series covering the last ``days`` calendar days (UTC),
    inclusive of today.

    - Real points are bucketed by their UTC calendar date and kept with their
      original ISO ``date`` string plus ``code``/``access_time``. A day may carry
      more than one real point (sorted ascending by timestamp).
    - Days with no data are emitted as a single null slot dated to midnight UTC
      of that day, kept in the same ISO ``...Z`` format as real points so the
      frontend can parse every entry uniformly:
      ``{"date": "YYYY-MM-DDT00:00:00Z", "code": None, "access_time": None}``.

    The result is ordered chronologically by construction.
    """
    now_utc = datetime.now(timezone.utc)
    today = now_utc.date()
    cutoff_date = (now_utc - timedelta(days=days)).date()

    # Bucket parseable, in-window real points by their UTC calendar date.
    by_day: dict = {}
    for item in availability or []:
        date_str = item.get("date")
        try:
            dt = _parse_iso_datetime(date_str)
        except Exception:
            logger.warning("Skipping availability point with unparseable date: %r", date_str)
            continue

        day = dt.date()
        if day < cutoff_date or day > today:
            continue

        by_day.setdefault(day, []).append((dt, {
            "date": date_str,
            "code": item.get("code"),
            "access_time": item.get("access_time"),
        }))

    # Walk every calendar day in the window, filling gaps with a null slot.
    series: list[dict] = []
    day = cutoff_date
    while day <= today:
        points = by_day.get(day)
        if points:
            points.sort(key=lambda pair: pair[0])
            series.extend(entry for _, entry in points)
        else:
            series.append({
                "date": day.strftime("%Y-%m-%dT00:00:00Z"),
                "code": None,
                "access_time": None,
            })
        day += timedelta(days=1)

    return series


async def _web_availability_last_days(request: URLRequest, days: int) -> dict:
    web_url = request.url.strip()
    if not web_url:
        raise HTTPException(status_code=422, detail="url must not be empty")

    doc = _get_availability_doc_by_url(web_url)
    if doc is None:
        raise HTTPException(status_code=404, detail="URL not found in availability collection")

    availability = (doc.get("data") or {}).get("availability") or []
    return {
        "url": doc.get("url", web_url),
        "availability": _build_daily_availability(availability, days),
    }


@router.post("/week", tags=["availability"])
async def web_availability_week(request: URLRequest):
    return await _web_availability_last_days(request, days=7)


@router.post("/month", tags=["availability"])
async def web_availability_month(request: URLRequest):
    return await _web_availability_last_days(request, days=30)


@router.post("/6months", tags=["availability"])
async def web_availability_6months(request: URLRequest):
    # rolling window approximation: 6 months ≈ 182 days
    return await _web_availability_last_days(request, days=182)
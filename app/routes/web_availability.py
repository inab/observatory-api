from datetime import datetime, timedelta, timezone
from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel
from app.helpers.database import connect_DB



router = APIRouter()

tools_collection, stats, pubs_collection, availability_collection = connect_DB()


class URLRequest(BaseModel):
    url: str


def _parse_iso_datetime(s: str) -> datetime:
    """
    Parse ISO datetime strings like:
      - 2024-06-02T02:17:39.932171Z
      - 2025-11-04T11:58:56.339012+00:00
    Returns a timezone-aware datetime in UTC.
    """
    if not s:
        raise ValueError("Empty date string")

    # Handle trailing 'Z' (Zulu/UTC)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # If somehow stored without tz, assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _get_availability_doc_by_url(web_url: str) -> dict | None:
    """
    Fetch minimal doc needed for availability response.
    Tries _id == url first, then url field.
    """
    doc = availability_collection.find_one(
        {"_id": web_url},
        projection={"_id": 0, "url": 1, "data.availability": 1},
    )
    if doc is None:
        doc = availability_collection.find_one(
            {"url": web_url},
            projection={"_id": 0, "url": 1, "data.availability": 1},
        )
    return doc


def _filter_availability_last_days(availability: list[dict], days: int) -> list[dict]:
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=days)

    filtered: list[dict] = []
    for item in availability or []:
        date_str = item.get("date")
        try:
            dt = _parse_iso_datetime(date_str)
        except Exception:
            continue

        if dt >= cutoff:
            filtered.append({
                "date": date_str,
                "code": item.get("code"),
                "access_time": item.get("access_time"),
            })

    filtered.sort(key=lambda x: _parse_iso_datetime(x["date"]))
    return filtered


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
        "availability": _filter_availability_last_days(availability, days),
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
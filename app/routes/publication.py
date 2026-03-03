from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.helpers.database import connect_DB
import re
from difflib import SequenceMatcher

router = APIRouter()

tools_collection, stats, pubs_collection, availability_collection = connect_DB()


class PublicationQuery(BaseModel):
    doi: Optional[str] = Field(default=None)
    pmid: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)


def _normalize_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.IGNORECASE)
    return doi.strip().lower()


def _norm_title(s: str) -> str:
    """Normalize titles for fuzzy matching."""
    s = (s or "").strip().lower()
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    # remove most punctuation (keep alphanumerics and spaces)
    s = re.sub(r"[^\w\s]", "", s)
    return s


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm_title(a), _norm_title(b)).ratio()


PROJECTION = {
    "_id": 0,
    "data": 1,
    "last_updated_at": 1,
    "updated_by": 1,
    "updated_logs": 1,
}


@router.post("/citations", tags=["publication"])
async def publication_citations(request: PublicationQuery):
    doi = request.doi.strip() if request.doi else None
    pmid = request.pmid.strip() if request.pmid else None
    title = request.title.strip() if request.title else None

    if not any([doi, pmid, title]):
        raise HTTPException(status_code=422, detail="Provide at least one of: doi, pmid, title")

    try:
        # 1) DOI preferred
        if doi:
            q: Dict[str, Any] = {"data.doi": _normalize_doi(doi)}
            doc = pubs_collection.find_one(q, projection=PROJECTION)
            if doc and doc.get("data") is not None:
                return {
                    "mode": "single",
                    "matched_by": "doi",
                    "doi": doi,
                    "item": doc["data"].get("citations"),
                }

        # 2) PMID next
        if pmid:
            q = {"data.pmid": pmid}
            doc = pubs_collection.find_one(q, projection=PROJECTION)
            if doc and doc.get("data") is not None:
                return {
                    "mode": "single",
                    "matched_by": "pmid",
                    "pmid": pmid,
                    "item": doc["data"].get("citations"),
                }

        # 3) Title fallback
        if title:
            exact_q = {"data.title": {"$regex": f"^{re.escape(title)}$", "$options": "i"}}

            # Pull up to 50 exact hits (if they exist), then decide
            exact_docs: List[Dict[str, Any]] = list(
                pubs_collection.find(exact_q, projection=PROJECTION).limit(50)
            )
            exact_docs = [d for d in exact_docs if d.get("data")]

            if len(exact_docs) == 1:
                return {
                    "mode": "single",
                    "matched_by": "title_exact",
                    "title": title,
                    "item": exact_docs[0]["data"].get("citations"),
                }

            if len(exact_docs) > 1:
                # Pick the closest match by fuzzy similarity against stored data.title
                best_doc = max(
                    exact_docs,
                    key=lambda d: _title_similarity(title, (d.get("data") or {}).get("title") or ""),
                )
                best_score = _title_similarity(title, (best_doc["data"].get("title") or ""))

                return {
                    "mode": "single",
                    "matched_by": "title_exact_multiple_best",
                    "title": title,
                    "match_score": round(best_score, 4),
                    "item": best_doc["data"].get("citations "),
                }

            # 3b) broad substring match -> keep list as you had
            broad_q = {"data.title": {"$regex": re.escape(title), "$options": "i"}}
            items = list(pubs_collection.find(broad_q, projection=PROJECTION).limit(50))
            items = [d for d in items if d.get("data")]

            if items:
                return {
                    "mode": "list",
                    "matched_by": "title_partial",
                    "title": title,
                    "count": len(items),
                    "items": [d["data"] for d in items],
                }

        raise HTTPException(status_code=404, detail="No publication metadata found for the given identifiers")

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Database query failed")
"""Authenticated operational endpoints.

Right now the only one is POST /admin/reindex, which lets the external import pipeline
build the MongoDB indexes on a freshly-built tools collection, before it promotes it
(`collection: "<tools>_next"`) or right after (no `collection`). That
collection is populated with plain inserts and so carries nothing but its default `_id`
index (the renamed `<tools>_archive_<run_id>` keeps the old ones), which breaks /search
with "text index required for $text query" and turns every filtered search into a
collection scan until the API is restarted. See app/helpers/indexes.py.

Deliberately no module-level connect_DB() here, unlike the other route modules:
ensure_indexes() opens and closes its own client per call, and keeping the import clean is
what lets the tests import this module with no MongoDB around.
"""
import hmac
import logging
import os
import threading
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from app.helpers.database import _load_config
from app.helpers.indexes import (
    CollectionNotAllowed,
    CollectionNotFound,
    ensure_indexes,
)

logger = logging.getLogger(__name__)

router = APIRouter()

ADMIN_TOKEN_ENV = "OBSERVATORY_ADMIN_TOKEN"

# auto_error=False so a missing/malformed header reaches us and we can answer 401
# (not authenticated) rather than HTTPBearer's default 403.
security = HTTPBearer(auto_error=False, description="Shared admin token.")

# A rebuild scans the whole collection when the text index has to be built, so a retry
# storm could pile several of them up. Per-process only: with multiple uvicorn workers
# each has its own lock, which is enough to stop one caller hammering the endpoint.
_reindex_lock = threading.Lock()


def _admin_token():
    """The configured admin secret, or None if this deployment has none.

    Resolved per request (not at import time) so the env var can be set late — in tests,
    and by a container that gets its environment after the image is built. Precedence
    matches app/helpers/database.py: environment first, then the CONFIG_PATH ini file.
    """
    token = os.getenv(ADMIN_TOKEN_ENV)
    if token:
        return token
    config = _load_config()
    if config.has_option("ADMIN", "ADMIN_TOKEN"):
        return config.get("ADMIN", "ADMIN_TOKEN") or None
    return None


def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Gate a route behind the shared admin token (`Authorization: Bearer <token>`)."""
    expected = _admin_token()
    if not expected:
        # Fail closed: an unconfigured secret must never mean "no authentication".
        raise HTTPException(
            status_code=503,
            detail=(
                "Admin endpoints are not configured on this deployment: set the "
                f"{ADMIN_TOKEN_ENV} environment variable or [ADMIN] ADMIN_TOKEN in the "
                "CONFIG_PATH ini file."
            ),
        )
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not hmac.compare_digest(credentials.credentials, expected):
        raise HTTPException(status_code=403, detail="Invalid admin token.")


class ReindexRequest(BaseModel):
    force_text: bool = Field(
        False,
        description=(
            "Drop and recreate the full-text index instead of leaving an existing one "
            "alone. Needed only after editing its fields or weights, since a text index "
            "cannot be redefined in place. Costs a full collection scan, and /search "
            "returns IndexNotFound for the duration of the rebuild."
        ),
    )
    collection: Optional[str] = Field(
        None,
        description=(
            "Tools collection to index. Omitted, the configured live one. The import "
            "pipeline names its staging collection (`<tools>_next`) so the indexes exist "
            "before it renames that into place. Only those two names are accepted (400 "
            "otherwise), and the collection must already exist (404 otherwise)."
        ),
    )


@router.post(
    "/reindex",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
    summary="Recreate the MongoDB indexes on the tools and stats collections",
    responses={
        400: {"description": "`collection` is not an indexable tools collection"},
        401: {"description": "Missing bearer token"},
        403: {"description": "Invalid admin token"},
        404: {"description": "`collection` does not exist"},
        409: {"description": "A rebuild is already in progress"},
        503: {"description": "No admin token configured on this deployment"},
    },
)
def reindex(body: Optional[ReindexRequest] = None):
    """Create any missing index on the tools and stats collections.

    Idempotent and cheap when everything already exists (`create_index` is a no-op then),
    so the import pipeline can call it unconditionally at the end of every run. The body is
    optional: POST with no payload at all is the same as `{"force_text": false}`.

    Unlike the startup path (`ensure_indexes_safe`), this one does not swallow errors — a
    Mongo or permission failure comes back as a 500 so the caller can decide what to do.
    """
    force_text = bool(body and body.force_text)
    collection = body.collection if body else None

    if not _reindex_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409, detail="An index rebuild is already in progress."
        )
    try:
        report = ensure_indexes(force_text=force_text, tools_collection=collection)
    except CollectionNotAllowed as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except CollectionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PyMongoError as exc:
        logger.exception("POST /admin/reindex failed")
        raise HTTPException(status_code=500, detail=f"Index creation failed: {exc}")
    finally:
        _reindex_lock.release()

    return {"force_text": force_text, **report}

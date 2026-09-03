"""Create all MongoDB indexes for an environment.

The API also ensures these indexes on startup (see app/helpers/indexes.py); this script
is the manual path — useful right after the import pipeline rebuilds the tools collection
without restarting the API, or to force the text index to be rebuilt with new
fields/weights (which the startup path deliberately never does).

The same rebuild is available remotely to the import pipeline as POST /admin/reindex
(app/routes/admin.py), which reports the same result.

Usage:
    CONFIG_PATH=./api-variables/config_db.ini python scripts/create_indexes.py
"""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.helpers.indexes import ensure_indexes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # force_text: drop and recreate the text index so edits to its fields/weights apply.
    report = ensure_indexes(force_text=True)
    print(json.dumps(report, indent=2))

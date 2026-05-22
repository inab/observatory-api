"""
Benchmark all API endpoints and report response times.

Usage:
    python scripts/benchmark.py                  # default: 3 runs, base http://localhost:3500
    python scripts/benchmark.py --runs 5
    python scripts/benchmark.py --base-url https://observatory.openebench.bsc.es/api
    python scripts/benchmark.py --filter search  # only cases whose name contains "search"
"""
import argparse
import statistics
import time
from typing import Any, Dict, Optional
import requests

BASE_URL = "http://localhost:3500"

# ---------------------------------------------------------------------------
# Test cases
# Each entry: (label, method, path, params, body)
# ---------------------------------------------------------------------------
CASES = [
    # ── /search ─────────────────────────────────────────────────────────────
    ("search: text only",              "GET",  "/search",         {"q": "blast"},                             None),
    ("search: text + source filter",   "GET",  "/search",         {"q": "alignment", "source": "biotools"},   None),
    ("search: text + type filter",     "GET",  "/search",         {"q": "assembly",  "type": "lib"},          None),
    ("search: text + license filter",  "GET",  "/search",         {"q": "blast",     "license": "MIT"},       None),
    ("search: multi-source filter",    "GET",  "/search",         {"q": "protein",   "source": "biotools,bioconda"}, None),
    ("search: page 0",                 "GET",  "/search",         {"q": "sequence",  "page": "0"},            None),
    ("search: page 1",                 "GET",  "/search",         {"q": "sequence",  "page": "1"},            None),
    ("search: filter-only (no q)",     "GET",  "/search",         {"source": "biotools", "type": "lib"},      None),

    # ── /initial-search ──────────────────────────────────────────────────────
    ("initial-search: all",            "GET",  "/initial-search", {},                                         None),
    ("initial-search: source",         "GET",  "/initial-search", {"source": "bioconda"},                     None),
    ("initial-search: type",           "GET",  "/initial-search", {"type": "web"},                            None),
    ("initial-search: license",        "GET",  "/initial-search", {"license": "MIT"},                         None),
    ("initial-search: page 2",         "GET",  "/initial-search", {"source": "biotools", "page": "2"},        None),
    ("initial-search: combined",       "GET",  "/initial-search", {"source": "biotools", "type": "lib"},      None),

    # ── /tool ────────────────────────────────────────────────────────────────
    ("tool: names_type_labels",        "GET",  "/tool/names_type_labels", {},                                 None),
    ("tool: detail by name",           "GET",  "/tool",           {"name": "blast2go"},                       None),

    # ── /fairsoft ────────────────────────────────────────────────────────────
    ("fairsoft: evaluate (minimal)",   "POST", "/fairsoft/evaluate", {}, {
        "tool_metadata": {
            "name": "blast",
            "type": ["web"],
            "repository": ["https://github.com/ncbi/blast_plus_docs"],
            "version_control": True,
        },
        "prepare": False,
    }),

    # ── /stats ───────────────────────────────────────────────────────────────
    ("stats: count_per_source",        "GET",  "/stats/tools/count_per_source",        {}, None),
    ("stats: count_total",             "GET",  "/stats/tools/count_total",             {}, None),
    ("stats: fair_scores_summary",     "GET",  "/stats/tools/fair_scores_summary",     {}, None),
    ("stats: fair_scores_means",       "GET",  "/stats/tools/fair_scores_means",       {}, None),
    ("stats: types_count",             "GET",  "/stats/tools/types_count",             {}, None),
    ("stats: documentation_coverage",  "GET",  "/stats/tools/documentation_coverage",  {}, None),
    ("stats: licenses_sunburst",       "GET",  "/stats/tools/licenses_summary_sunburst", {}, None),
]


def run_case(
    base_url: str,
    method: str,
    path: str,
    params: Dict[str, Any],
    body: Optional[Dict],
    runs: int,
) -> Dict:
    url = base_url.rstrip("/") + path
    times = []
    status = None
    error = None

    for _ in range(runs):
        try:
            start = time.perf_counter()
            if method == "GET":
                r = requests.get(url, params=params, timeout=30)
            else:
                r = requests.post(url, json=body, timeout=30)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            times.append(elapsed)
            status = r.status_code
        except Exception as e:
            error = str(e)
            break

    return {
        "times": times,
        "status": status,
        "error": error,
        "min": min(times) if times else None,
        "avg": statistics.mean(times) if times else None,
        "max": max(times) if times else None,
    }


def _bar(ms: float, scale: float = 1.5) -> str:
    """Simple ASCII bar proportional to response time."""
    filled = min(int(ms / scale), 60)
    return "█" * filled


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--filter", default="", help="Only run cases whose label contains this string")
    args = parser.parse_args()

    cases = CASES
    if args.filter:
        cases = [c for c in cases if args.filter.lower() in c[0].lower()]

    print(f"\nBenchmarking {len(cases)} endpoints × {args.runs} runs  →  {args.base_url}\n")
    print(f"{'Label':<44} {'Status':>6}  {'Min':>7}  {'Avg':>7}  {'Max':>7}  Chart")
    print("─" * 100)

    for label, method, path, params, body in cases:
        result = run_case(args.base_url, method, path, params, body, args.runs)

        if result["error"]:
            print(f"{label:<44} {'ERR':>6}  {result['error']}")
            continue

        status = result["status"]
        status_str = str(status)
        avg = result["avg"]
        flag = " ⚠" if avg > 2000 else ("  " if avg < 500 else "  ")

        print(
            f"{label:<44} {status_str:>6}  "
            f"{result['min']:>6.0f}ms  {avg:>6.0f}ms  {result['max']:>6.0f}ms  "
            f"{_bar(avg)}{flag}"
        )

    print("─" * 100)
    print("⚠  = avg > 2 s\n")


if __name__ == "__main__":
    main()

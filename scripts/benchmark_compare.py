"""
Compare response times between two base URLs (e.g. before vs after adding indexes).

Usage:
    python scripts/benchmark_compare.py <url-a> <url-b>
    python scripts/benchmark_compare.py http://localhost:3500 https://observatory.openebench.bsc.es/api
    python scripts/benchmark_compare.py --runs 5 --filter search <url-a> <url-b>
"""
import argparse
import statistics
import sys
import time
from typing import Any, Dict, Optional
import requests

sys.path.insert(0, __file__.rsplit("/scripts", 1)[0])
from scripts.benchmark import CASES


def measure(
    base_url: str,
    method: str,
    path: str,
    params: Dict[str, Any],
    body: Optional[Dict],
    runs: int,
) -> Dict:
    url = base_url.rstrip("/") + path
    times = []

    for _ in range(runs):
        try:
            start = time.perf_counter()
            if method == "GET":
                r = requests.get(url, params=params, timeout=30)
            else:
                r = requests.post(url, json=body, timeout=30)
            times.append((time.perf_counter() - start) * 1000)
        except Exception as e:
            return {"avg": None, "error": str(e)}

    return {
        "avg": statistics.mean(times),
        "min": min(times),
        "max": max(times),
        "status": r.status_code,
        "error": None,
    }


def _bar(ms: float, width: int = 30, scale: float = 3.0) -> str:
    filled = min(int(ms / scale), width)
    return ("█" * filled).ljust(width)


def _delta_str(a: float, b: float) -> str:
    if a == 0:
        return "  n/a"
    diff = b - a
    pct = (diff / a) * 100
    sign = "+" if diff >= 0 else ""
    return f"{sign}{pct:+.0f}%"


def _speedup(a: float, b: float) -> str:
    """Express B relative to A: '2.1× faster' or '1.3× slower'."""
    if b == 0 or a == 0:
        return ""
    ratio = a / b
    if ratio >= 1.05:
        return f"  {ratio:.1f}× faster ✓"
    elif ratio <= 0.95:
        return f"  {1/ratio:.1f}× slower ✗"
    return "  ~same"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url_a", help="First base URL (baseline)")
    parser.add_argument("url_b", help="Second base URL (comparison)")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--filter", default="", help="Only run cases whose label contains this string")
    parser.add_argument("--label-a", default=None, help="Display name for URL A")
    parser.add_argument("--label-b", default=None, help="Display name for URL B")
    args = parser.parse_args()

    label_a = args.label_a or args.url_a
    label_b = args.label_b or args.url_b

    cases = CASES
    if args.filter:
        cases = [c for c in cases if args.filter.lower() in c[0].lower()]

    # Truncate labels for display
    la = label_a[:28]
    lb = label_b[:28]

    header_w = 42
    col_w = 32

    print(f"\nComparing {len(cases)} endpoints × {args.runs} runs\n")
    print(f"  A: {label_a}")
    print(f"  B: {label_b}\n")
    print(f"{'':>{header_w}}  {'A (avg)':>8}  {la:<{col_w}}  {'B (avg)':>8}  {lb:<{col_w}}  Delta")
    print("─" * (header_w + 2 + 10 + col_w + 10 + col_w + 12))

    total_a, total_b, regressions = [], [], []

    for label, method, path, params, body in cases:
        ra = measure(args.url_a, method, path, params, body, args.runs)
        rb = measure(args.url_b, method, path, params, body, args.runs)

        if ra["error"] or rb["error"]:
            err = ra["error"] or rb["error"]
            print(f"  {label:<{header_w}}  ERROR: {err}")
            continue

        avg_a, avg_b = ra["avg"], rb["avg"]
        total_a.append(avg_a)
        total_b.append(avg_b)

        if avg_b > avg_a * 1.1:
            regressions.append(label)

        delta = _delta_str(avg_a, avg_b)
        speedup = _speedup(avg_a, avg_b)

        print(
            f"  {label:<{header_w}}"
            f"  {avg_a:>6.0f}ms  {_bar(avg_a, col_w)}"
            f"  {avg_b:>6.0f}ms  {_bar(avg_b, col_w)}"
            f"  {delta}{speedup}"
        )

    print("─" * (header_w + 2 + 10 + col_w + 10 + col_w + 12))

    if total_a and total_b:
        sum_a, sum_b = sum(total_a), sum(total_b)
        print(f"\n  {'Total time (sum of avgs)':<{header_w}}  {sum_a:>6.0f}ms{' ' * (col_w + 2)}  {sum_b:>6.0f}ms  {_speedup(sum_a, sum_b)}")
        print(f"  {'Mean per endpoint':<{header_w}}  {statistics.mean(total_a):>6.0f}ms{' ' * (col_w + 2)}  {statistics.mean(total_b):>6.0f}ms")

    if regressions:
        print(f"\n  ✗ Regressions (B > A by >10%):")
        for r in regressions:
            print(f"    - {r}")

    print()


if __name__ == "__main__":
    main()

"""
Phase 6 performance smoke test script.

Usage:
1. Start backend server (uvicorn app.main:app --reload)
2. Ensure a user and company profile exist
3. Run: python tests/performance_smoke_test.py --token <JWT>
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests

BASE_URL = "http://localhost:8000/api"
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"


def timed_request(method, url, **kwargs):
    start = time.perf_counter()
    response = requests.request(method, url, timeout=180, **kwargs)
    elapsed = time.perf_counter() - start
    return response, elapsed


def main(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    invoices_path = SAMPLE_DIR / "invoices.csv"
    gstr2b_path = SAMPLE_DIR / "gstr2b.json"

    if not invoices_path.exists() or not gstr2b_path.exists():
        raise SystemExit("Sample data not found. Run tests/generate_sample_data.py first.")

    with invoices_path.open("rb") as f:
        response, elapsed = timed_request(
            "POST",
            f"{BASE_URL}/upload/invoices",
            headers=headers,
            data={"turnover_slab": "1.5cr_to_5cr"},
            files={"file": ("invoices.csv", f, "text/csv")},
        )
    print(f"Invoice upload: {elapsed:.2f}s status={response.status_code}")

    with gstr2b_path.open("rb") as f:
        response, elapsed = timed_request(
            "POST",
            f"{BASE_URL}/upload/gstr2b",
            headers=headers,
            files={"file": ("gstr2b.json", f, "application/json")},
        )
    print(f"GSTR-2B upload: {elapsed:.2f}s status={response.status_code}")

    response, elapsed = timed_request("POST", f"{BASE_URL}/reconcile/run", headers=headers)
    print(f"Reconciliation run: {elapsed:.2f}s status={response.status_code}")

    response, elapsed = timed_request("GET", f"{BASE_URL}/dashboard/metrics", headers=headers)
    print(f"Dashboard metrics: {elapsed:.2f}s status={response.status_code}")

    if response.ok:
        print("Dashboard payload:")
        print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="JWT access token")
    args = parser.parse_args()
    main(args.token)

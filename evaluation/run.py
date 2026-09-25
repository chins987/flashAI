from __future__ import annotations

import json
import sys
from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:8000/api/tasks"
CASES_DIR = Path(__file__).parent / "cases"


def load_cases():
    cases = []

    for path in sorted(CASES_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        cases.append({
            "name": path.stem,
            "task": data["task"],
            "expected": data["expected"],
        })

    return cases


def get_actual(response):
    decision = response.get("decision")

    if decision == "ACCEPT":
        return "ACCEPT"

    if decision == "HOLD":
        return "HOLD"

    if decision == "CLARIFY":
        return "CLARIFY"

    return decision or "UNKNOWN"


def run_case(case):
    try:
        response = requests.post(
            BASE_URL,
            json={"task": case["task"]},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        actual = get_actual(data)
        expected = case["expected"]

        passed = actual == expected

        return {
            "name": case["name"],
            "expected": expected,
            "actual": actual,
            "passed": passed,
        }

    except Exception as exc:
        return {
            "name": case["name"],
            "expected": case["expected"],
            "actual": "ERROR",
            "passed": False,
            "error": str(exc),
        }


def main():
    print()
    print("=" * 60)
    print("VERITASMESH EVALUATION")
    print("=" * 60)

    cases = load_cases()

    if not cases:
        print("No evaluation cases found.")
        sys.exit(1)

    results = []

    for case in cases:
        print(f"\nRunning: {case['name']}")

        result = run_case(case)
        results.append(result)

        if result["passed"]:
            print(
                f"PASS  Expected={result['expected']} "
                f"Actual={result['actual']}"
            )
        else:
            print(
                f"FAIL  Expected={result['expected']} "
                f"Actual={result['actual']}"
            )

            if "error" in result:
                print(f"      Error: {result['error']}")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    accuracy = (passed / total) * 100

    print()
    print("-" * 60)
    print(f"RESULT: {passed}/{total} cases passed")
    print(f"VERIFICATION ACCURACY: {accuracy:.1f}%")
    print("-" * 60)

    if passed == total:
        print("ALL EVALUATION CASES PASSED")
    else:
        print("SOME EVALUATION CASES FAILED")

    print("=" * 60)


if __name__ == "__main__":
    main()
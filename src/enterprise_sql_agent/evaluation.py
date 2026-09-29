"""Offline evaluation runner for the constrained analytics planner."""

from __future__ import annotations

import json
from pathlib import Path

from .service import AnalyticsService


def evaluate(service: AnalyticsService, dataset: Path) -> dict[str, object]:
    cases = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines() if line]
    results: list[dict[str, object]] = []
    for case in cases:
        response = service.ask(case["question"])
        passed = (
            response["plan_id"] == case["expected_plan"]
            and response["rows"]
            and response["rows"][0].get(case["expected_field"]) == case["expected_value"]
        )
        results.append(
            {
                "id": case["id"],
                "passed": bool(passed),
                "expected_plan": case["expected_plan"],
                "actual_plan": response["plan_id"],
            }
        )
    passed_cases = sum(item["passed"] for item in results)
    return {
        "total_cases": len(results),
        "passed_cases": passed_cases,
        "pass_rate": passed_cases / len(results) if results else 0.0,
        "results": results,
    }

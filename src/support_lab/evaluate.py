"""Evaluate deterministic decisions against declared synthetic expectations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import SupportCase
from .rules import decide


EVALUATED_FIELDS = ("intent", "risk", "ai_eligibility", "required_source", "route")


def evaluate_case(record: dict[str, Any]) -> dict[str, Any]:
    decision = decide(SupportCase.from_dict(record))
    expected = record.get("expected", {})
    actual = decision.to_dict()
    mismatches = {
        field: {"expected": expected.get(field), "actual": actual.get(field)}
        for field in EVALUATED_FIELDS
        if expected.get(field) != actual.get(field)
    }
    return {
        "case_id": decision.case_id,
        "passed": not mismatches,
        "mismatches": mismatches,
        "decision": actual,
    }


def evaluate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = [evaluate_case(record) for record in records]
    passed = sum(result["passed"] for result in results)
    return {
        "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed},
        "results": results,
    }


def load_records(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("Case file must contain a JSON list")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("data/synthetic_cases.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = evaluate_records(load_records(args.cases))
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if report["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

import json
import unittest
from pathlib import Path

from support_lab.evaluate import evaluate_records


ROOT = Path(__file__).resolve().parents[1]


class EvaluationTests(unittest.TestCase):
    def test_checked_in_cases_match_declared_expectations(self):
        records = json.loads((ROOT / "data" / "synthetic_cases.json").read_text(encoding="utf-8"))
        report = evaluate_records(records)
        self.assertEqual(report["summary"]["failed"], 0, report)
        self.assertEqual(report["summary"]["total"], len(records))


if __name__ == "__main__":
    unittest.main()

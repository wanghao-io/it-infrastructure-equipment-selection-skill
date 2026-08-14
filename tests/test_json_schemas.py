from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_json_schemas import validate, validate_catalog, validate_retrospective_semantics  # noqa: E402


class JsonSchemaContractTests(unittest.TestCase):
    def test_all_catalog_examples_validate(self) -> None:
        self.assertEqual(validate_catalog(ROOT), [])

    def test_server_rfq_rejects_unknown_and_missing_fields(self) -> None:
        schema = json.loads((ROOT / "schemas/server-rfq.schema.json").read_text(encoding="utf-8"))
        instance = json.loads((ROOT / "assets/server-rfq-example.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(instance)
        del broken["quotes"][0]["supplier"]
        broken["quotes"][0]["mystery_discount"] = -10
        errors = validate(broken, schema)
        self.assertTrue(any("supplier" in error and "required" in error for error in errors))
        self.assertTrue(any("mystery_discount" in error and "not allowed" in error for error in errors))

    def test_hci_rejects_fractional_nodes_and_string_boolean(self) -> None:
        schema = json.loads((ROOT / "schemas/hci-failover.schema.json").read_text(encoding="utf-8"))
        instance = json.loads((ROOT / "assets/hci-failover-example.json").read_text(encoding="utf-8"))
        instance["nodes"] = 4.9
        instance["storage_protection_valid"] = "true"
        errors = validate(instance, schema)
        self.assertTrue(any("nodes" in error and "integer" in error for error in errors))
        self.assertTrue(any("storage_protection_valid" in error and "boolean" in error for error in errors))

    def test_retrospective_cannot_claim_settlement_without_numeric_record(self) -> None:
        schema = json.loads((ROOT / "schemas/project-retrospective.schema.json").read_text(encoding="utf-8"))
        case = json.loads((ROOT / "examples/real-project-retrospectives/manufacturing-scada-budget-revision.json").read_text(encoding="utf-8"))
        case["budget"]["settled"] = "unknown"
        self.assertTrue(any("settled" in error for error in validate(case, schema)))

    def test_retrospective_evidence_cannot_exceed_project_stage(self) -> None:
        case = json.loads((ROOT / "examples/real-project-retrospectives/manufacturing-scada-budget-revision.json").read_text(encoding="utf-8"))
        case["evidence_status"] = "settlement-record"
        errors = validate_retrospective_semantics(case)
        self.assertTrue(any("exceeds project_stage" in error for error in errors))
        self.assertTrue(any("budget.settled" in error for error in errors))

    def test_operational_claim_requires_structured_measurements(self) -> None:
        case = json.loads((ROOT / "examples/real-project-retrospectives/manufacturing-scada-budget-revision.json").read_text(encoding="utf-8"))
        case["project_stage"] = "operational"
        case["evidence_status"] = "operational-measurement"
        self.assertTrue(any("operational_measurements" in error for error in validate_retrospective_semantics(case)))

    def test_v2_forecast_comparison_requires_scope_normalization(self) -> None:
        case = json.loads((ROOT / "examples/real-project-retrospectives/v2-design-baseline-example.json").read_text(encoding="utf-8"))
        case.update({"project_stage": "awarded", "evidence_status": "award-record", "budget": {
            "revised": 100, "awarded": 90, "currency": "CNY"
        }})
        errors = validate_retrospective_semantics(case)
        self.assertTrue(any("technical_scope_normalized" in error for error in errors))
        self.assertTrue(any("commercial_scope_normalized" in error for error in errors))

    def test_price_decision_strict_contract_fails_before_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps({"schema_version": 1, "items": [{"mystery": 1}]}), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/normalize_price_evidence.py"),
                str(path), "--summary", "--strict-contract",
            ], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("$.items[0]", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_unversioned_price_input_requires_explicit_legacy_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.json"
            path.write_text("[]", encoding="utf-8")
            rejected = subprocess.run([
                sys.executable, str(ROOT / "scripts/normalize_price_evidence.py"), str(path), "--summary",
            ], cwd=ROOT, text=True, capture_output=True)
            allowed = subprocess.run([
                sys.executable, str(ROOT / "scripts/normalize_price_evidence.py"),
                str(path), "--summary", "--legacy-input",
            ], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("unversioned price input is deprecated", rejected.stderr)
        self.assertEqual(allowed.returncode, 0)
        self.assertIn("WARNING", allowed.stderr)


if __name__ == "__main__":
    unittest.main()

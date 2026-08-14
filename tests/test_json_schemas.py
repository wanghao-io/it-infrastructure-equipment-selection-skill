from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_json_schemas import validate, validate_catalog  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()

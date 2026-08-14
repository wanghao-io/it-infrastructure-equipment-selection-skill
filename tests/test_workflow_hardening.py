from __future__ import annotations

import sys
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from calculate_budget import calculate as budget  # noqa: E402
from calculate_tco import calculate as tco  # noqa: E402
from evaluate_architecture import evaluate  # noqa: E402
from generate_tender_spec import generate as tender  # noqa: E402
from generate_topology import mermaid  # noqa: E402
from normalize_price_evidence import select_budget_anchor  # noqa: E402


class WorkflowHardeningTests(unittest.TestCase):
    def test_three_end_to_end_project_prompts_execute_critical_workflows(self):
        cases = json.loads((ROOT / "tests/scenarios/end-to-end-projects.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 3)
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            utf8_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

            scada_input = tmp / "scada.json"
            scada_input.write_text(json.dumps({"scada_io_points": 3000}), encoding="utf-8")
            discovery = json.loads(subprocess.check_output([
                sys.executable, str(ROOT / "scripts/guide_requirements.py"),
                "--scenario", "manufacturing-scada-small", "--input", str(scada_input),
            ], env=utf8_env))
            self.assertFalse(discovery["ready_for_architecture"])
            self.assertIn("historian_points", discovery["missing_required_fields"])

            hci = json.loads(subprocess.check_output([
                sys.executable, str(ROOT / "scripts/calculate_hci_failover.py"),
                str(ROOT / "assets/hci-failover-example.json"),
            ], env=utf8_env))
            self.assertEqual(hci["status"], "PASS")
            tco_result = subprocess.check_output([
                sys.executable, str(ROOT / "scripts/calculate_tco.py"),
                str(ROOT / "assets/tco-example.json"), "--format", "markdown",
            ], env=utf8_env).decode("utf-8")
            self.assertIn("Infrastructure TCO", tco_result)

            weak = tmp / "weak-prices.json"
            weak.write_text(json.dumps({"schema_version": 1, "items": [{
                "candidate": "same-family starting price", "product_class": "configurable-enterprise",
                "configuration": "partial configuration", "source_type": "market-aggregator",
                "source_date": "2026-08-12", "as_of_date": "2026-08-12", "quote_current": True,
                "comparable": True, "configuration_match_score": 0.75, "price": 47000,
                "currency": "CNY", "quote_mode": "starting-price",
            }]}), encoding="utf-8")
            revision = json.loads(subprocess.check_output([
                sys.executable, str(ROOT / "scripts/normalize_price_evidence.py"), str(weak),
                "--summary", "--strict-contract", "--existing-budget", "92000", "--product-class", "configurable-enterprise",
            ], env=utf8_env))
            self.assertEqual(revision["budget_revision"]["decision"], "hold-existing-provisional")
    def test_tbd_tco_stays_incomplete_without_crashing(self):
        result = tco({"electricity_rate_per_kwh": 0, "candidates": [{"name": "A", "purchase_cost": 1, "one_time_implementation": 0, "annual_support": "TBD", "annual_license": 0, "annual_facility": 0, "annual_other_opex": 0}]})
        self.assertIsNone(result["results"][0]["total_tco"])

    def test_bom_tbd_is_not_silently_zero(self):
        result = budget([{"Quantity": 2, "Unit Price": "TBD"}], 10)
        self.assertEqual(result["status"], "incomplete-needs-confirmation")
        self.assertIsNone(result["total_with_contingency"])

    def test_tender_output_order_is_deterministic(self):
        data = {"requirements": [{"id": "R2", "requirement": "B"}, {"id": "R1", "requirement": "A"}]}
        output = tender(data)
        self.assertLess(output.rfind("| R2 |"), output.rfind("| R1 |"))

    def test_unknown_topology_zone_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown zone"):
            mermaid({"zones": [], "devices": [{"id": "a", "zone": "missing"}], "links": []})

    def test_string_boolean_in_architecture_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "JSON boolean"):
            evaluate({"hci_required": "false"})

    def test_mixed_currency_anchor_is_rejected(self):
        base = {"configuration": "fixed SKU", "source_type": "retail-exact-sku", "source_date": "2026-08-12", "quote_current": True, "comparable": True, "exact_configuration_match": True, "price": 100}
        result = select_budget_anchor([{**base, "candidate": "A", "currency": "CNY"}, {**base, "candidate": "B", "currency": "USD"}])
        self.assertEqual(result["status"], "needs-confirmation")


if __name__ == "__main__":
    unittest.main()

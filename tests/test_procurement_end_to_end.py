from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict:
    output = subprocess.check_output(
        [sys.executable, *args],
        cwd=ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        text=True,
    )
    return json.loads(output)


class ProcurementWorkflowEndToEndTests(unittest.TestCase):
    def test_inquiry_budget_revision_and_hci_outputs_execute_end_to_end(self) -> None:
        scenarios = {
            case["name"]: case
            for case in json.loads(
                (ROOT / "tests/scenarios/end-to-end-projects.json").read_text(encoding="utf-8")
            )
        }
        self.assertIn("server-rfq", scenarios["manufacturing-scada-single-server"]["expected"])
        self.assertIn("budget-revision-guard", scenarios["enterprise-server-budget-revision"]["expected"])
        self.assertIn("hci-n-plus-one", scenarios["hospital-hci-n-plus-one"]["expected"])

        inquiry = run_json(
            str(ROOT / "scripts/compare_server_quotes.py"),
            str(ROOT / "assets/server-rfq-example.json"),
        )
        self.assertEqual(inquiry["status"], "ready")
        self.assertEqual(inquiry["independent_quote_count"], 2)
        self.assertEqual(inquiry["confidence_level"], "High")
        self.assertTrue(all(row["eligible_for_pricing"] for row in inquiry["quotes"]))
        self.assertEqual((inquiry["market_low"], inquiry["market_high"]), (110000.0, 112000.0))
        self.assertEqual(inquiry["budget_control_high"], 117600.0)

        rfq = json.loads((ROOT / "assets/server-rfq-example.json").read_text(encoding="utf-8"))
        evidence = []
        for quote in rfq["quotes"]:
            evidence.append({
                **quote,
                "candidate": quote["supplier"],
                "product_class": "configurable-enterprise",
                "source_type": "authorized-reseller-quote",
                "as_of_date": rfq["requirement"]["as_of_date"],
                "quote_current": True,
                "comparable": True,
                "exact_configuration_match": True,
                "technical_fit_status": "PASS",
                "eligible_for_pricing": True,
                "price_scope_complete": True,
            })

        with tempfile.TemporaryDirectory() as directory:
            evidence_file = Path(directory) / "validated-quotes.json"
            evidence_file.write_text(json.dumps({"items": evidence}), encoding="utf-8")
            revision = run_json(
                str(ROOT / "scripts/normalize_price_evidence.py"),
                str(evidence_file),
                "--summary",
                "--existing-budget", "130000",
                "--product-class", "configurable-enterprise",
            )["budget_revision"]

        self.assertEqual(revision["decision"], "revise-to-current-anchor")
        self.assertEqual(revision["recommended_budget_low"], inquiry["market_low"])
        self.assertEqual(revision["recommended_budget_high"], inquiry["market_high"])
        self.assertEqual(revision["budget_anchor"]["anchor_count"], 2)

        hci = run_json(
            str(ROOT / "scripts/calculate_hci_failover.py"),
            str(ROOT / "assets/hci-failover-example.json"),
        )
        self.assertEqual(hci["status"], "PASS")
        self.assertEqual(hci["policy"], "N+1")
        self.assertEqual(hci["remaining_nodes"], 3)
        self.assertTrue(hci["eligible_for_final_design"])
        self.assertEqual(
            set(hci["dimension_checks"]),
            {"cpu_cores", "memory_gb", "usable_storage_tb", "storage_iops", "network_gbps"},
        )
        self.assertTrue(all(check["pass"] for check in hci["dimension_checks"].values()))


if __name__ == "__main__":
    unittest.main()

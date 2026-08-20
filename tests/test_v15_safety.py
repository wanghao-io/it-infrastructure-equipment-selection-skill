from __future__ import annotations

import json
import math
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from calculate_hci_failover import calculate as hci_calculate  # noqa: E402
from calculate_server_capacity import calculate_virtualization  # noqa: E402
from calculate_network_ports import calculate as network_calculate  # noqa: E402
from calculate_storage import raid_usable_capacity  # noqa: E402
from calculate_tco import calculate as tco_calculate  # noqa: E402
from calculate_ups import calculate as ups_calculate  # noqa: E402
from compare_vendors import build_report  # noqa: E402
from evaluate_architecture import evaluate  # noqa: E402
from guide_requirements import analyze_requirements, load_templates  # noqa: E402
from generate_bom import generate  # noqa: E402
from normalize_price_evidence import assess_budget_revision, select_budget_anchor  # noqa: E402
from validate_json_schemas import validate_file  # noqa: E402


class V15SafetyTests(unittest.TestCase):
    def test_schema_and_tco_reject_non_finite_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nan-tco.json"
            path.write_text('{"electricity_rate_per_kwh": NaN, "candidates": []}', encoding="utf-8")
            errors = validate_file(ROOT / "schemas/tco.schema.json", path)
        self.assertTrue(any("non-standard JSON" in error for error in errors))
        with self.assertRaisesRegex(ValueError, "finite"):
            tco_calculate({"electricity_rate_per_kwh": math.nan, "candidates": [{}]})

    def test_integer_resources_round_up(self) -> None:
        result = calculate_virtualization(1, 1.1, 1.1, cpu_overcommit=1, cpu_headroom=0.25, memory_headroom=0.25)
        self.assertEqual(result["estimated_physical_cpu_cores"], 2)
        self.assertEqual(result["estimated_memory_gb"], 2)

    def test_public_calculators_reject_non_finite_values(self) -> None:
        for operation in (
            lambda: raid_usable_capacity(4, math.nan, "10"),
            lambda: network_calculate(10, spare_ratio=math.nan),
            lambda: ups_calculate(math.inf),
        ):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(ValueError, "finite"):
                    operation()

    def test_network_downlinks_are_not_blended_with_separate_uplinks(self) -> None:
        result = network_calculate(48, uplinks=2, spare_ratio=0)
        self.assertEqual(result["required_downlink_ports"], 48)
        self.assertEqual(result["single_switch_port_class"], 48)
        self.assertTrue(result["candidate_port_layout_confirmation_required"])

    def test_empty_architecture_input_remains_unresolved(self) -> None:
        result = evaluate({})
        self.assertEqual(result["input_status"], "CONDITIONAL")
        self.assertEqual(result["hci"]["decision"], "unresolved")
        self.assertEqual(result["firewall"]["decision"], "unresolved")

    def test_public_scenario_template_example_executes(self) -> None:
        data = load_templates(ROOT / "assets/scenario-template-example.json")
        result = analyze_requirements("example:industrial-edge", template_data=data)
        self.assertIn("control_criticality", result["missing_required_fields"])

    def test_mixed_product_classes_and_override_conflicts_hold_budget(self) -> None:
        base = {
            "configuration": "synthetic", "source_type": "authorized-reseller-quote",
            "source_date": "2026-08-20", "as_of_date": "2026-08-20", "quote_current": True,
            "comparable": True, "exact_configuration_match": True, "technical_fit_status": "PASS",
            "eligible_for_pricing": True, "currency": "CNY", "price": 90,
            "supplier": "Supplier A", "sales_channel": "authorized",
        }
        mixed = [
            {**base, "candidate": "server", "product_class": "configurable-enterprise"},
            {**base, "candidate": "marker", "product_class": "fixed-sku", "price": 95},
        ]
        self.assertEqual(select_budget_anchor(mixed)["status"], "needs-confirmation")
        conflict = assess_budget_revision(
            100, [mixed[0]], product_class="fixed-sku", existing_currency="CNY"
        )
        self.assertEqual(conflict["decision"], "hold-existing-provisional")
        self.assertIn("conflicts", conflict["reason"])

    def test_budget_revision_requires_matching_baseline_currency(self) -> None:
        item = {
            "candidate": "switch", "product_class": "fixed-sku", "configuration": "exact",
            "source_type": "retail-exact-sku", "source_date": "2026-08-20", "as_of_date": "2026-08-20",
            "quote_current": True, "comparable": True, "exact_configuration_match": True,
            "technical_fit_status": "PASS", "eligible_for_pricing": True,
            "currency": "CNY", "price": 90, "source": "store",
        }
        self.assertEqual(assess_budget_revision(100, [item])["decision"], "hold-existing-provisional")
        mismatch = assess_budget_revision(100, [item], existing_currency="USD")
        self.assertEqual(mismatch["decision"], "hold-existing-provisional")
        self.assertIn("currencies differ", mismatch["reason"])

    def test_hci_v1_arithmetic_never_claims_final_design(self) -> None:
        data = json.loads((ROOT / "assets/hci-failover-example.json").read_text(encoding="utf-8"))
        result = hci_calculate(data)
        self.assertEqual(result["capacity_check_status"], "PASS")
        self.assertFalse(result["eligible_for_final_design"])
        self.assertEqual(result["final_design_status"], "CONDITIONAL")

    def test_server_rfq_v2_example_validates(self) -> None:
        errors = validate_file(
            ROOT / "schemas/v2/server-rfq.schema.json", ROOT / "assets/server-rfq-v2-example.json"
        )
        self.assertEqual(errors, [])

    def test_duplicate_vendor_names_do_not_cross_wire_gates(self) -> None:
        report = build_report({
            "criteria": [{"key": "fit", "name": "Fit", "weight": 1}],
            "candidates": [
                {"candidate_id": "a", "name": "Same", "scores": {"fit": {"score": 8}}, "gates": [{"status": "PASS", "requirement": "R"}]},
                {"candidate_id": "b", "name": "Same", "scores": {"fit": {"score": 2}}, "gates": [{"status": "FAIL", "requirement": "R"}]},
            ],
        })
        self.assertEqual(report.count("### Same — PASS"), 1)
        self.assertEqual(report.count("### Same — FAIL"), 1)

    def test_reference_example_does_not_default_hci(self) -> None:
        text = (ROOT / "examples/industrial-scada-hci-reference-design.md").read_text(encoding="utf-8")
        self.assertNotIn("推荐采用三节点超融合架构", text)
        self.assertIn("HCI is not a default", text)

    def test_v15_evaluation_fixtures_cover_ten_independent_failures(self) -> None:
        cases = json.loads((ROOT / "tests/scenarios/v15-evaluations.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["required_routes"])
            self.assertGreaterEqual(len(case["blocking_criteria"]), 2)

    def test_bom_union_fields_and_non_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bom.csv"
            generate([{"name": "A", "qty": 1}, {"name": "B", "license": "L"}], str(output))
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertIn("license", rows[0])
            self.assertEqual(rows[1]["license"], "L")
            with self.assertRaises(FileExistsError):
                generate([{"name": "C"}], str(output))


if __name__ == "__main__":
    unittest.main()

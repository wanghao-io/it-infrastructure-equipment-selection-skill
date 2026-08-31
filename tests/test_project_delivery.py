from __future__ import annotations

import copy
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from calculate_budget import calculate
from compare_server_quotes import compare
from validate_server_quote import validate_quote
from drawio_tools import create, compare_presentations, clone_group, semantic_snapshot
from project_records import check_record, guarded_path, preflight, write_new


def example(name):
    return json.loads((ROOT / "assets" / f"{name}-example.json").read_text())


def invoke(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                          text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})


class QuoteAndBudgetRepairTests(unittest.TestCase):
    def test_seeded_permutation_and_arithmetic_properties(self):
        import random
        rng = random.Random(20260831)
        case = example("server-rfq-v2")
        for _ in range(40):
            quotes = copy.deepcopy(case["quotes"])
            rng.shuffle(quotes)
            result = compare(case["requirement"], quotes, contract_version=2)
            self.assertEqual((result["market_low"], result["market_high"]), (110000, 112000))
            qty, price = rng.randint(1, 100), rng.randint(1, 10000)
            self.assertEqual(calculate([{"qty": qty, "unit_price": price, "total": qty * price}], 0)["subtotal"], qty * price)
            self.assertIsNone(calculate([{"qty": qty, "unit_price": price, "total": qty * price + 1}], 0)["subtotal"])

    def test_r01_upgraded_configuration_is_not_exact_anchor(self):
        case = example("server-rfq-v2")
        case["quotes"][1]["configuration"].update(cpu_socket_count=4, dimm_count=16)
        result = compare(case["requirement"], case["quotes"], contract_version=2)
        self.assertEqual(result["independent_quote_count"], 1)
        self.assertEqual(result["confidence_level"], "Medium")
        self.assertEqual(result["quotes"][1]["technical_fit_status"], "PASS")
        self.assertFalse(result["quotes"][1]["exact_configuration_match"])

    def test_r02_scope_id_cannot_mask_commercial_difference(self):
        for fields in ({"tax_included": False}, {"tax_basis": "VAT excluded"}, {"delivery_basis": "EXW"}):
            with self.subTest(fields=fields):
                case = example("server-rfq-v2")
                case["quotes"][1].update(fields)
                result = compare(case["requirement"], case["quotes"], contract_version=2)
                self.assertEqual(result["status"], "needs-confirmation")
                self.assertNotIn("market_low", result)

    def test_missing_is_conditional_not_failed_technical_evidence(self):
        case = example("server-rfq-v2")
        case["quotes"][0]["configuration"].pop("nic_model")
        result = validate_quote(case["requirement"], case["quotes"][0], contract_version=2)
        self.assertEqual(result["technical_fit_status"], "CONDITIONAL")
        self.assertFalse(result["eligible_for_pricing"])

    def test_r03_conflicting_line_total_does_not_enter_subtotal(self):
        result = calculate([{"qty": 2, "unit_price": 100, "total": 1}], 0)
        self.assertEqual(result["status"], "incomplete-needs-confirmation")
        self.assertIsNone(result["subtotal"])
        self.assertEqual(result["conflicts"][0]["difference"], -199)
        self.assertEqual(result["conflicts"][0]["row"], 1)

    def test_decimal_rounding_and_explicit_lump_sum(self):
        self.assertEqual(calculate([{"qty": 3, "unit_price": 0.1, "total": 0.3}], 0)["subtotal"], 0.3)
        row = {"qty": 2, "unit_price": 100, "total": 180, "pricing_basis": "lump-sum", "pricing_note": "Approved package discount"}
        self.assertEqual(calculate([row], 0)["subtotal"], 180)
        row.pop("pricing_note")
        self.assertIsNone(calculate([row], 0)["subtotal"])

    def test_r04_draft_cli_writes_tbd_not_zero(self):
        with tempfile.TemporaryDirectory() as td:
            path, out = Path(td) / "input.json", Path(td) / "bom.csv"
            path.write_text(json.dumps([{"name": "AP", "qty": "TBD", "unit_price": "TBD"}]))
            result = invoke("scripts/generate_bom.py", str(path), str(out), "--stage", "draft")
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertIsNone(summary["total_with_contingency"])
            self.assertFalse(summary["procurement_ready"])
            with out.open(encoding="utf-8-sig") as f:
                self.assertEqual(next(csv.DictReader(f))["qty"], "TBD")
            result = invoke("scripts/generate_bom.py", str(path), str(Path(td) / "final.csv"))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(td) / "final.csv").exists())


class ProjectEvidenceTests(unittest.TestCase):
    def test_r05_conflicting_versions_do_not_choose_latest(self):
        data = example("project-evidence")
        fact = copy.deepcopy(data["facts"][0])
        fact.update(id="F2", value=99)
        data["facts"].append(fact)
        result = check_record(data, "project-evidence")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("conflicting-active-facts", [f["code"] for f in result["findings"]])

    def test_r06_approval_is_field_scoped(self):
        data = example("project-evidence")
        fact = copy.deepcopy(data["facts"][0])
        fact.update(id="F2", field="protocol", value="Modbus", status="known", supersedes=["F1"], approval_ref="user-confirmed-connection-only")
        data["facts"][0]["status"] = "superseded"
        data["facts"].append(fact)
        codes = [f["code"] for f in check_record(data, "project-evidence")["findings"]]
        self.assertIn("invalid-field-supersession", codes)
        self.assertIn("source-not-authoritative-for-field", codes)

    def test_r07_protected_path_and_input_are_never_written(self):
        data = example("project-evidence")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for target in ("../escaped.txt", "other-agent-output/a.txt", "source.csv"):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    write_new(Path(target), "content", root=root, manifest=data)
            write_new(Path("out/a.txt"), "content", root=root, manifest=data)
            with self.assertRaises(FileExistsError):
                write_new(Path("out/a.txt"), "replacement", root=root, manifest=data)
            self.assertEqual((root / "out/a.txt").read_text(), "content")

    def test_r07_symlink_escape_is_rejected(self):
        data = example("project-evidence")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "other-agent-output").mkdir()
            try:
                (root / "out").symlink_to(root / "other-agent-output", target_is_directory=True)
            except OSError:
                self.skipTest("host does not allow symlinks")
            with self.assertRaisesRegex(ValueError, "protected"):
                guarded_path(root, data, "out/a.txt", write=True)
            self.assertFalse((root / "other-agent-output/a.txt").exists())

    def test_explicit_source_hash_checks_do_not_scan_other_files(self):
        import hashlib
        data = example("project-evidence")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.csv").write_bytes(b"source")
            data["sources"][0]["sha256"] = hashlib.sha256(b"source").hexdigest()
            result = check_record(data, "project-evidence", project_root=root, check_files=True)
            self.assertNotIn("source-changed-since-baseline", [f["code"] for f in result["findings"]])
            (root / "source.csv").write_bytes(b"changed")
            result = check_record(data, "project-evidence", project_root=root, check_files=True)
            self.assertIn("source-changed-since-baseline", [f["code"] for f in result["findings"]])

    def test_future_version_and_unknown_fields_fail_before_checks(self):
        for mutation in ({"schema_version": 2}, {"schema_version": True}, {"custom_fields": {}}):
            data = example("project-evidence")
            data.update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                check_record(data, "project-evidence")


class DeliveryTests(unittest.TestCase):
    def test_unknown_endpoints_are_not_reported_as_zero_total(self):
        data = example("project-delivery")
        data["assets"][0]["endpoint_ports"] = None
        result = check_record(data, "project-delivery")
        self.assertIsNone(result["metrics"]["declared_endpoint_ports"])
        self.assertEqual(result["metrics"]["known_endpoint_ports"], 3)
        self.assertEqual(result["status"], "CONDITIONAL")

    def test_disconnected_network_asset_is_not_silently_complete(self):
        data = example("project-delivery")
        data["links"] = [link for link in data["links"] if link["source"] != "AP"]
        result = check_record(data, "project-delivery")
        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertIn("network-asset-has-no-declared-link", [f["code"] for f in result["findings"]])

    def test_valid_delivery_executes_through_public_cli(self):
        result = invoke("scripts/infra_cli.py", "project-check", "project-delivery", "assets/project-delivery-example.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertFalse(data["procurement_ready"])
        self.assertEqual(data["metrics"]["capacity_checks"]["poe"]["required"], 48)

    def test_r08_endpoint_pool_is_distinct_from_group_quantity(self):
        data = example("project-delivery")
        data["assets"][0]["quantity"] = 14
        data["bom"][0]["quantity"] = 14
        data["representations"][0]["devices"][0]["quantity"] = 14
        # endpoint_ports is explicitly the group TOTAL, not one port per machine.
        result = check_record(data, "project-delivery")
        self.assertEqual(result["metrics"]["declared_endpoint_ports"], 4)

    def test_r09_cable_cores_do_not_establish_protocol(self):
        data = example("project-delivery")
        data["links"][0].update(medium="instrument-cable", cable_cores=5, protocol=None)
        result = check_record(data, "project-delivery")
        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertIsNone(data["links"][0]["protocol"])

    def test_r10_cable_reserve_is_monotonic_and_unverified_stays_estimate(self):
        data = example("project-delivery")
        length = dict(path_m=20, vertical_m=3, termination_m=2, detour_m=5, waste_ratio=0.1, round_to_m=5, unit_verified=False, basis="drawing-route")
        data["links"][0]["length"] = length
        link_id = data["links"][0]["id"]
        first = check_record(data, "project-delivery")
        length["waste_ratio"] = 0.3
        second = check_record(data, "project-delivery")
        self.assertGreater(second["metrics"]["estimated_cable_lengths_m"][link_id], first["metrics"]["estimated_cable_lengths_m"][link_id])
        self.assertEqual(second["status"], "CONDITIONAL")

    def test_r11_presentation_change_preserves_semantics(self):
        before = create(example("project-delivery"))
        after = before.replace('x="80"', 'x="160"').replace("#e6f1ff", "#ffffff")
        result = compare_presentations(before, after)
        self.assertTrue(result["semantic_equal"])
        self.assertEqual(result["visual_qa"], "NOT_RUN")
        after = before.replace('source="asset:CTRL"', 'source="asset:GW"')
        self.assertFalse(compare_presentations(before, after)["semantic_equal"])

    def test_icon_clone_keeps_all_descendants(self):
        root = ET.fromstring('<root><mxCell id="g" parent="1"/><mxCell id="c" parent="g"/><mxCell id="d" parent="c"/></root>')
        cloned = clone_group(root, "g", "new-")
        self.assertEqual({n.get("id") for n in cloned}, {"new-g", "new-c", "new-d"})
        self.assertEqual(next(n for n in cloned if n.get("id") == "new-d").get("parent"), "new-c")

    def test_r12_missing_required_material_and_license_is_detected(self):
        data = example("project-delivery")
        data["bom"][-1]["quantity"] = 1
        data["links"][0]["materials"] = [{"bom_line_id": "missing-optics", "quantity": 2}]
        result = check_record(data, "project-delivery")
        codes = [f["code"] for f in result["findings"]]
        self.assertIn("material-or-license-shortfall:B-AC-LIC", codes)
        self.assertIn("material-or-license-shortfall:missing-optics", codes)

    def test_r13_phase_and_model_projection_drift_fails(self):
        for mutation in ({"phase_id": "future"}, {"model": "different"}, {"quantity": 3}, {"disposition": "future"}):
            data = example("project-delivery")
            data["representations"][0]["devices"][0].update(mutation)
            with self.subTest(mutation=mutation):
                self.assertEqual(check_record(data, "project-delivery")["status"], "FAIL")

    def test_drawing_creation_is_non_overwriting_and_baseline_bound(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "manifest.json").write_text(json.dumps(example("project-evidence")))
            (root / "delivery.json").write_text(json.dumps(example("project-delivery")))
            args = ("scripts/drawio_tools.py", "create", "delivery.json", "out/topology.drawio", "--manifest", str(root / "manifest.json"), "--project-root", str(root))
            result = invoke(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(semantic_snapshot((root / "out/topology.drawio").read_text()))
            self.assertNotEqual(invoke(*args).returncode, 0)


class AcceptanceTests(unittest.TestCase):
    def passed_record(self):
        data = example("acceptance-evidence")
        data.pop("point_ledger")
        data.pop("license")
        data["records"][0].update(result="PASS", stage="native", simulation_only=False,
                                  native_result="PASS", evidence_refs=["synthetic-test-log"],
                                  expected_count=5, tested_count=5, unverified=[])
        return data

    def test_r15_adapter_pass_is_not_native_pass(self):
        data = self.passed_record()
        data["records"][0].update(claim="native-compatibility", adapter_used=True, adapter_ref="type-adapter-v1", native_result="FAIL")
        self.assertEqual(check_record(data, "acceptance-evidence")["status"], "FAIL")
        data["records"][0]["claim"] = "scoped-test"
        self.assertEqual(check_record(data, "acceptance-evidence")["status"], "PASS")
        self.assertEqual(data["records"][0]["native_result"], "FAIL")

    def test_r16_system_points_cannot_be_ignored_for_license(self):
        data = example("acceptance-evidence")
        data["point_ledger"].update(required_business_io=3000, charged_system_points=38, license_capacity=3000)
        self.assertIn("production-license-capacity-shortfall", [f["code"] for f in check_record(data, "acceptance-evidence")["findings"]])

    def test_r17_sample_cannot_prove_all_points(self):
        data = self.passed_record()
        data["records"][0].update(claim="all-points", expected_count=3000, tested_count=2)
        self.assertEqual(check_record(data, "acceptance-evidence")["status"], "FAIL")
        data = example("acceptance-evidence")
        data["point_ledger"].update(required_business_io=3000, mapped_io=0, good_io=0)
        codes = [f["code"] for f in check_record(data, "acceptance-evidence")["findings"]]
        self.assertIn("coverage-incomplete:mapped_io", codes)

    def test_r18_boot_and_mock_do_not_prove_business_recovery(self):
        data = self.passed_record()
        data["records"][0].update(stage="smoke", claim="business-recovery")
        self.assertEqual(check_record(data, "acceptance-evidence")["status"], "FAIL")
        data["license"] = dict(kind="trial", expires_on="2026-01-01", perpetual=False, evidence_ref="synthetic-license")
        self.assertIn("license-expired", [f["code"] for f in check_record(data, "acceptance-evidence")["findings"]])

    def test_unknown_claim_and_unproven_pass_fail(self):
        data = self.passed_record()
        data["records"][0]["evidence_refs"] = []
        self.assertEqual(check_record(data, "acceptance-evidence")["status"], "FAIL")
        data["records"][0]["claim"] = "certified-everything"
        with self.assertRaises(ValueError):
                check_record(data, "acceptance-evidence")

    def test_missing_count_is_unknown_not_a_false_source_conflict(self):
        data = example("acceptance-evidence")
        data["point_ledger"]["declared_source_count"] = None
        codes = [f["code"] for f in check_record(data, "acceptance-evidence")["findings"]]
        self.assertIn("point-count-basis-unresolved", codes)
        self.assertNotIn("source-export-count-mismatch", codes)


if __name__ == "__main__":
    unittest.main()

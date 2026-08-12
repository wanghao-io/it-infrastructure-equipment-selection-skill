from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from calculate_hci_failover import calculate  # noqa: E402


class HciFailoverTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((ROOT / "assets/hci-failover-example.json").read_text(encoding="utf-8"))

    def test_all_dimensions_and_failure_domains_pass(self):
        result = calculate(self.case)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(set(result["dimension_checks"]), {"cpu_cores", "memory_gb", "usable_storage_tb", "storage_iops", "network_gbps"})

    def test_memory_shortfall_fails_design(self):
        self.case["workload_demand"]["memory_gb"] = 700
        result = calculate(self.case)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["dimension_checks"]["memory_gb"]["pass"])

    def test_storage_protection_is_a_mandatory_gate(self):
        self.case["storage_protection_valid"] = False
        self.assertEqual(calculate(self.case)["status"], "FAIL")

    def test_string_boolean_is_rejected(self):
        self.case["network_redundancy_valid"] = "true"
        with self.assertRaisesRegex(ValueError, "JSON boolean"):
            calculate(self.case)

    def test_fractional_node_count_is_rejected(self):
        self.case["nodes"] = 4.9
        with self.assertRaisesRegex(ValueError, "integer"):
            calculate(self.case)

    def test_legacy_wrapper_is_covered(self):
        from calculate_hci_failover import check_n_plus_one
        self.assertTrue(check_n_plus_one(4, 100, 512))
        self.assertFalse(check_n_plus_one(2, 100, 512))


if __name__ == "__main__":
    unittest.main()

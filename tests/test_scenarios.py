#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from calculate_historian import calculate as calculate_historian  # noqa: E402
from calculate_network_ports import calculate as calculate_network_ports  # noqa: E402
from calculate_server_capacity import calculate_services  # noqa: E402
from calculate_storage import raid_usable_capacity  # noqa: E402
from calculate_ups import calculate as calculate_ups  # noqa: E402
from evaluate_architecture import evaluate  # noqa: E402


class ArchitectureRegressionTests(unittest.TestCase):
    def test_core_scenarios(self) -> None:
        scenarios = json.loads((ROOT / "tests" / "scenarios" / "core-regressions.json").read_text(encoding="utf-8"))
        for scenario in scenarios:
            with self.subTest(scenario=scenario["name"]):
                result = evaluate(scenario["requirements"])
                expected = scenario["expect"]

                if "hci" in expected:
                    self.assertEqual(result["hci"]["decision"], expected["hci"])
                if "aggregation_core" in expected:
                    self.assertEqual(result["aggregation_core"]["decision"], expected["aggregation_core"])
                if "layer3_routing" in expected:
                    self.assertEqual(result["layer3_routing"]["decision"], expected["layer3_routing"])
                if "firewall" in expected:
                    self.assertEqual(result["firewall"]["decision"], expected["firewall"])
                if "domestic_xinchuang" in expected:
                    self.assertEqual(result["domestic_xinchuang"]["decision"], expected["domestic_xinchuang"])

                controls = result["single_server_controls"]
                for key in ("raid", "ups_graceful_shutdown", "independent_backup"):
                    if key in expected:
                        self.assertEqual(controls[key], expected[key])

                if "remote_control_required_controls" in expected:
                    actual = result["ot_remote_control"]["required_controls"]
                    for control in expected["remote_control_required_controls"]:
                        self.assertIn(control, actual)


class SizingRegressionTests(unittest.TestCase):
    def test_raid10_capacity(self) -> None:
        self.assertEqual(raid_usable_capacity(4, 4, "10"), 8)

    def test_historian_estimate_is_positive(self) -> None:
        result = calculate_historian(2000, 5, compression_factor=0.5, retention_days=365)
        self.assertGreater(result["recommended_online_capacity_tb"], 0)
        self.assertLess(result["recommended_online_capacity_tb"], 10)

    def test_ups_reports_w_and_va(self) -> None:
        result = calculate_ups(600, power_factor=0.9, capacity_margin=1.3, runtime_minutes=10)
        self.assertGreaterEqual(result["minimum_output_w_with_margin"], 780)
        self.assertGreater(result["minimum_va_with_margin"], result["minimum_output_w_with_margin"])

    def test_inter_vlan_requires_l3(self) -> None:
        result = calculate_network_ports(30, spare_ratio=0.2, vlan_count=5, inter_vlan_communication_required=True)
        self.assertTrue(result["layer3_routing_required"])
        self.assertEqual(result["single_switch_port_class"], 48)

    def test_consolidated_services_respect_minimums(self) -> None:
        services = [
            {"name": "scada", "cpu_cores": 2, "memory_gb": 12},
            {"name": "historian", "cpu_cores": 4, "memory_gb": 32},
            {"name": "bi", "cpu_cores": 2, "memory_gb": 16},
        ]
        result = calculate_services(services, minimum_cpu_cores=12, minimum_memory_gb=96)
        self.assertGreaterEqual(result["recommended_cpu_cores"], 12)
        self.assertGreaterEqual(result["recommended_memory_gb"], 96)


if __name__ == "__main__":
    unittest.main()

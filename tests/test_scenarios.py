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
from normalize_price_evidence import (  # noqa: E402
    configuration_match_score,
    evidence_priority,
    normalize,
    select_budget_anchor,
)


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


class PricingRegressionTests(unittest.TestCase):
    def _exact_match(self) -> dict[str, float]:
        return {
            "cpu": 1.0,
            "memory": 1.0,
            "ssd": 1.0,
            "hdd": 1.0,
            "raid": 1.0,
            "network": 1.0,
            "power": 1.0,
            "warranty": 1.0,
            "tax": 1.0,
            "accessories": 1.0,
        }

    def test_exact_configuration_scores_one(self) -> None:
        item = {"configuration_match": self._exact_match()}
        self.assertEqual(configuration_match_score(item), 1.0)

    def test_missing_major_components_reduce_match_score(self) -> None:
        item = {
            "configuration_match": {
                "cpu": 1.0,
                "memory": 1.0,
                "ssd": 0.2,
                "hdd": 0.0,
                "raid": 0.0,
                "network": 1.0,
                "power": 1.0,
                "warranty": 0.5,
                "tax": 0.0,
                "accessories": 0.0,
            }
        }
        self.assertLess(configuration_match_score(item), 0.70)

    def test_exact_current_quote_has_higher_priority_than_historical(self) -> None:
        exact = {
            "source_type": "authorized-reseller-quote",
            "quote_current": True,
            "configuration_match": self._exact_match(),
            "comparable": True,
        }
        historical = {
            "source_type": "government-award",
            "quote_current": False,
            "configuration_match_score": 0.90,
            "comparable": True,
        }
        self.assertLess(evidence_priority(exact), evidence_priority(historical))

    def test_market_aggregator_is_context_not_exact_quote(self) -> None:
        aggregator = {
            "source_type": "market-aggregator",
            "quote_current": True,
            "configuration_match_score": 0.98,
            "comparable": True,
        }
        exact_quote = {
            "source_type": "official-store-human-quote",
            "quote_current": True,
            "configuration_match_score": 0.98,
            "comparable": True,
        }
        self.assertEqual(evidence_priority(aggregator), 6)
        self.assertEqual(evidence_priority(exact_quote), 1)

    def test_fixed_sku_exact_market_quote_can_be_priority_two(self) -> None:
        item = {
            "product_class": "fixed-sku",
            "source_type": "enterprise-marketplace-exact-sku",
            "quote_current": True,
            "configuration_match_score": 1.0,
            "comparable": True,
        }
        self.assertEqual(evidence_priority(item), 2)

    def test_starting_price_is_excluded_for_configurable_enterprise(self) -> None:
        item = {
            "candidate": "Starting price",
            "product_class": "configurable-enterprise",
            "configuration": "same chassis family, base configuration",
            "source_type": "market-aggregator",
            "quote_mode": "starting-price",
            "source_date": "2026-08-12",
            "quote_current": True,
            "price": 48000,
            "configuration_match_score": 0.95,
            "starting_price_or_base_config": True,
            "comparable": True,
        }
        row = normalize([item])[0]
        self.assertFalse(row["anchor_eligible"])
        self.assertIn("starting-or-base-configuration-price", row["anchor_exclusion_reasons"])
        self.assertIn("configurable-enterprise-requires-config-level-price", row["anchor_exclusion_reasons"])

    def test_exact_quotes_define_budget_anchor_not_old_lower_price(self) -> None:
        base = {
            "product_class": "configurable-enterprise",
            "configuration": "full enterprise server configuration",
            "source_date": "2026-08-12",
            "quote_current": True,
            "tax_included": True,
            "price_scope_complete": True,
            "orderability_confirmed": True,
            "comparable": True,
        }
        items = [
            {
                **base,
                "candidate": "Quote A",
                "source_type": "official-store-human-quote",
                "quote_mode": "human-configured",
                "hardware_price": 89000,
                "configuration_match": self._exact_match(),
            },
            {
                **base,
                "candidate": "Quote B",
                "source_type": "authorized-reseller-quote",
                "quote_mode": "exact-config",
                "hardware_price": 91500,
                "configuration_match": self._exact_match(),
            },
            {
                "candidate": "Historical lower price",
                "product_class": "configurable-enterprise",
                "configuration": "similar but not exact server configuration",
                "source_type": "government-award",
                "quote_mode": "historical-transaction",
                "source_date": "2025-04-01",
                "quote_current": False,
                "hardware_price": 65000,
                "tax_included": True,
                "configuration_match_score": 0.88,
                "comparable": True,
            },
            {
                "candidate": "Bare chassis listing",
                "product_class": "configurable-enterprise",
                "configuration": "bare chassis",
                "source_type": "generic-listing",
                "quote_mode": "base-config-listing",
                "source_date": "2026-08-12",
                "quote_current": True,
                "hardware_price": 48000,
                "tax_included": False,
                "configuration_match_score": 0.40,
                "starting_price_or_base_config": True,
                "comparable": False,
            },
        ]

        result = select_budget_anchor(items)
        self.assertEqual(result["preferred_evidence_priority"], 1)
        self.assertEqual(result["recommended_budget_low"], 89000)
        self.assertEqual(result["recommended_budget_high"], 91500)
        self.assertEqual(result["historical_context_low"], 65000)
        self.assertGreaterEqual(result["lower_priority_evidence_excluded_from_anchor"], 1)
        self.assertGreaterEqual(result["excluded_signal_count"], 1)
        self.assertEqual(result["confidence"], "Market-verified / Exact-config")
        self.assertEqual(result["confidence_level"], "High")

    def test_single_exact_quote_requests_second_quote(self) -> None:
        item = {
            "candidate": "Single quote",
            "product_class": "configurable-enterprise",
            "configuration": "full enterprise server configuration",
            "source_type": "manufacturer-direct-quote",
            "quote_mode": "human-configured",
            "source_date": "2026-08-12",
            "quote_current": True,
            "orderability_confirmed": True,
            "price_scope_complete": True,
            "hardware_price": 90000,
            "tax_included": True,
            "configuration_match": self._exact_match(),
            "comparable": True,
        }
        result = select_budget_anchor([item])
        self.assertTrue(result["needs_second_quote"])
        self.assertEqual(result["recommended_budget_low"], 90000)
        self.assertEqual(result["recommended_budget_high"], 90000)
        self.assertEqual(result["confidence_level"], "Medium")


if __name__ == "__main__":
    unittest.main()

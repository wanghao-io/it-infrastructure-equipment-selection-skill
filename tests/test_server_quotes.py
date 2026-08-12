from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_server_quotes import compare  # noqa: E402
from validate_server_quote import validate_quote  # noqa: E402


class ServerQuoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads((ROOT / "assets/server-rfq-example.json").read_text(encoding="utf-8"))

    def test_two_valid_quotes_create_control_range(self):
        result = compare(self.case["requirement"], self.case["quotes"])
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["independent_quote_count"], 2)
        self.assertEqual(result["confidence_level"], "High")
        self.assertGreater(result["budget_control_high"], result["market_high"])

    def test_configuration_shortfall_is_not_price_eligible(self):
        quote = dict(self.case["quotes"][0])
        quote["configuration"] = dict(quote["configuration"], memory_gb=128)
        result = validate_quote(self.case["requirement"], quote)
        self.assertEqual(result["technical_fit_status"], "FAIL")
        self.assertFalse(result["eligible_for_pricing"])

    def test_missing_commercial_scope_is_not_zero(self):
        quote = dict(self.case["quotes"][0])
        quote.pop("required_licenses")
        result = validate_quote(self.case["requirement"], quote)
        self.assertIsNone(result["normalized_comparable_cost"])
        self.assertIn("required_licenses", result["missing_commercial_fields"])

    def test_string_boolean_is_rejected(self):
        quote = dict(self.case["quotes"][0], orderability_confirmed="false")
        with self.assertRaisesRegex(ValueError, "JSON boolean"):
            validate_quote(self.case["requirement"], quote)

    def test_two_quote_ids_from_same_supplier_are_one_independent_source(self):
        first = dict(self.case["quotes"][0])
        second = dict(first, quote_id="Q-A-SECOND")
        result = compare(self.case["requirement"], [first, second])
        self.assertEqual(result["independent_quote_count"], 1)
        self.assertEqual(result["confidence_level"], "Medium")

    def test_negative_risk_reserve_is_rejected(self):
        requirement = dict(self.case["requirement"], risk_reserve_percent=-20)
        with self.assertRaisesRegex(ValueError, "risk_reserve_percent"):
            compare(requirement, self.case["quotes"])

    def test_stale_server_quote_is_not_eligible(self):
        quote = dict(self.case["quotes"][0], source_date="2020-01-01", quote_valid_until="2026-09-12")
        result = validate_quote(self.case["requirement"], quote)
        self.assertFalse(result["eligible_for_pricing"])
        self.assertIn("quote-stale-or-future-dated", result["reasons"])

    def test_missing_supplier_identity_is_rejected(self):
        quote = dict(self.case["quotes"][0])
        quote.pop("supplier")
        result = validate_quote(self.case["requirement"], quote)
        self.assertFalse(result["eligible_for_pricing"])
        self.assertIn("supplier", result["missing_commercial_fields"])

    def test_incomplete_server_baseline_is_rejected(self):
        requirement = dict(self.case["requirement"], required_configuration={"cpu_cores": 24})
        with self.assertRaisesRegex(ValueError, "baseline fields"):
            validate_quote(requirement, self.case["quotes"][0])

    def test_string_configuration_boolean_does_not_pass(self):
        quote = dict(self.case["quotes"][0])
        quote["configuration"] = dict(quote["configuration"], redundant_power="true")
        result = validate_quote(self.case["requirement"], quote)
        self.assertEqual(result["technical_fit_status"], "FAIL")

    def test_duplicate_supplier_uses_conservative_higher_quote(self):
        first = dict(self.case["quotes"][0])
        second = dict(first, quote_id="Q-A-HIGH", hardware_price=120000)
        result = compare(self.case["requirement"], [first, second])
        self.assertEqual(result["independent_quote_count"], 1)
        self.assertEqual(result["market_high"], 130000.0)


if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

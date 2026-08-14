#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from calculate_ups import assess_candidate  # noqa: E402


class SpecificationFirstPricingTests(unittest.TestCase):
    def test_1500va_900w_candidate_fails_when_real_power_is_too_low(self) -> None:
        result = assess_candidate(
            800,
            900,
            1500,
            runtime_minutes=10,
            runtime_curve_verified=True,
            shutdown_interface_verified=True,
        )
        self.assertEqual(result["status"], "not-eligible-for-pricing")
        self.assertFalse(result["capacity_checks"]["output_w_ok"])
        self.assertIn("candidate-output-W-below-required-margin", result["reasons"])

    def test_capacity_alone_does_not_make_candidate_price_eligible(self) -> None:
        result = assess_candidate(
            600,
            1200,
            1500,
            runtime_minutes=10,
            runtime_curve_verified=False,
            shutdown_interface_verified=True,
        )
        self.assertEqual(result["status"], "not-eligible-for-pricing")
        self.assertIn("runtime-curve-not-verified-at-protected-load", result["reasons"])

    def test_fully_verified_candidate_can_enter_price_comparison(self) -> None:
        result = assess_candidate(
            600,
            1200,
            1500,
            runtime_minutes=10,
            runtime_curve_verified=True,
            shutdown_interface_verified=True,
        )
        self.assertEqual(result["status"], "eligible-for-pricing")
        self.assertTrue(result["eligible_for_pricing"])
        self.assertEqual(result["reasons"], [])

    def test_router_preserves_technical_fit_and_bom_claim_routes(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("INV-TECH-BEFORE-PRICE", skill)
        self.assertIn("eligible_for_pricing=true", skill)
        self.assertIn("references/ups-sizing.md", skill)
        self.assertIn("references/bom-checklist.md", skill)
        bom = (ROOT / "references" / "bom-checklist.md").read_text(encoding="utf-8")
        self.assertIn("## Commercial Claim Boundary", bom)

    def test_ups_reference_forbids_price_driven_resizing(self) -> None:
        ref = (ROOT / "references" / "ups-sizing.md").read_text(encoding="utf-8")
        self.assertIn("Do not let a cheaper UPS redefine the project requirement", ref)
        self.assertIn("1500VA/900W", ref)
        self.assertIn("eligible-for-pricing", ref)


if __name__ == "__main__":
    unittest.main()

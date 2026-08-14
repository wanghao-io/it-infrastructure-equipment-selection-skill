#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalize_price_evidence import assess_budget_revision, normalize, select_budget_anchor  # noqa: E402


SERVER_CONFIG = "2U; 1x4410Y; 128GB; 2x960GB SSD; 2x1.92TB SSD; 4x4TB HDD; RAID cache/PLP; dual PSU"


class BudgetRevisionGuardrailTests(unittest.TestCase):
    def test_fixed_sku_cannot_be_lowered_without_technical_fit(self) -> None:
        item = {
            "candidate": "Cheap fixed SKU", "product_class": "fixed-sku",
            "configuration": "exact SKU", "source_type": "retail-exact-sku",
            "source_date": "2026-08-12", "quote_current": True,
            "comparable": True, "exact_configuration_match": True,
            "currency": "CNY", "price": 50,
        }
        result = assess_budget_revision(100, [item])
        self.assertEqual(result["decision"], "hold-existing-provisional")
        self.assertIn("technical fit", result["reason"])

    def test_fixed_sku_without_gate_cannot_be_any_budget_anchor(self) -> None:
        item = {
            "candidate": "Ungated fixed SKU", "product_class": "fixed-sku",
            "configuration": "exact SKU", "source_type": "retail-exact-sku",
            "source_date": "2026-08-12", "as_of_date": "2026-08-12",
            "quote_current": True, "comparable": True,
            "exact_configuration_match": True, "currency": "CNY", "price": 100,
        }
        row = normalize([item])[0]
        self.assertFalse(row["anchor_eligible"])
        self.assertIn("technical-fit-not-pass", row["anchor_exclusion_reasons"])
        self.assertIn("technical-fit-not-eligible-for-pricing", row["anchor_exclusion_reasons"])
        self.assertEqual(select_budget_anchor([item])["status"], "needs-confirmation")

    def test_same_supplier_multiple_quote_ids_count_once(self) -> None:
        base = {
            "product_class": "fixed-sku", "configuration": "exact SKU",
            "source_type": "authorized-reseller-quote", "source_date": "2026-08-12",
            "as_of_date": "2026-08-12", "quote_current": True,
            "comparable": True, "exact_configuration_match": True,
            "technical_fit_status": "PASS", "eligible_for_pricing": True,
            "currency": "CNY", "sales_channel": "Authorized",
        }
        anchor = select_budget_anchor([
            {**base, "candidate": "q1", "supplier": " Supplier A ", "quote_id": "q1", "price": 90},
            {**base, "candidate": "q2", "supplier": "supplier a", "quote_id": "q2", "price": 92},
        ])
        self.assertEqual(anchor["anchor_count"], 1)
        self.assertEqual(anchor["confidence_level"], "Medium")
        self.assertTrue(anchor["needs_second_quote"])

    def test_different_decision_scopes_are_rejected(self) -> None:
        base = {
            "product_class": "fixed-sku", "configuration": "exact SKU",
            "source_type": "retail-exact-sku", "source_date": "2026-08-12",
            "as_of_date": "2026-08-12", "quote_current": True,
            "comparable": True, "exact_configuration_match": True,
            "technical_fit_status": "PASS", "eligible_for_pricing": True,
            "currency": "CNY", "price": 100,
        }
        anchor = select_budget_anchor([
            {**base, "candidate": "switch", "decision_scope_id": "bom-switch-1", "source": "A"},
            {**base, "candidate": "ap", "decision_scope_id": "bom-ap-1", "source": "B"},
        ])
        self.assertEqual(anchor["status"], "needs-confirmation")
        self.assertIn("different decision_scope_id", anchor["reason"])

    def test_declared_evidence_level_cannot_override_derived_result(self) -> None:
        item = {
            "candidate": "Self-declared", "product_class": "fixed-sku",
            "configuration": "SKU", "source_type": "retail-exact-sku",
            "source_date": "2026-08-12", "as_of_date": "2026-08-12",
            "quote_current": True, "comparable": True, "exact_configuration_match": True,
            "currency": "CNY", "price": 100, "evidence_level": "Verified",
        }
        row = normalize([item])[0]
        self.assertNotIn("evidence_level", row)
        self.assertEqual(row["declared_evidence_level"], "Verified")
        self.assertEqual(row["derived_evidence_level"], "Needs confirmation")

    def test_overlapping_lower_range_still_requires_technical_fit(self) -> None:
        base = {
            "product_class": "fixed-sku", "configuration": "exact SKU",
            "source_type": "retail-exact-sku", "source_date": "2026-08-12",
            "as_of_date": "2026-08-12", "quote_current": True,
            "comparable": True, "exact_configuration_match": True,
            "currency": "CNY",
        }
        result = assess_budget_revision(100, [
            {**base, "candidate": "lower", "price": 90},
            {**base, "candidate": "higher", "price": 110},
        ])
        self.assertEqual(result["decision"], "hold-existing-provisional")
        self.assertEqual(result["recommended_budget_low"], 100.0)

    def test_tbd_commercial_cost_is_excluded_not_zero(self) -> None:
        item = {
            "candidate": "Incomplete quote", "product_class": "configurable-enterprise",
            "configuration": SERVER_CONFIG, "source_type": "official-store-human-quote",
            "source_date": "2026-08-12", "quote_current": True, "comparable": True,
            "exact_configuration_match": True, "technical_fit_status": "PASS",
            "eligible_for_pricing": True, "orderability_confirmed": True,
            "price_scope_complete": True, "tax_included": True, "currency": "CNY",
            "price": 50000, "mandatory_accessories": "TBD", "required_licenses": 0,
            "warranty_support": 0, "required_implementation": 0, "tax_amount": 0, "shipping": 0,
        }
        anchor = select_budget_anchor([item])
        self.assertEqual(anchor["status"], "needs-confirmation")
        row = normalize([item])[0]
        self.assertIsNone(row["normalized_comparable_cost"])
        self.assertIn("invalid-commercial-field:mandatory_accessories", row["anchor_exclusion_reasons"])

    def test_stale_self_declared_current_quote_is_excluded(self) -> None:
        item = {
            "candidate": "Old quote", "product_class": "fixed-sku", "configuration": "SKU",
            "source_type": "retail-exact-sku", "source_date": "2020-01-01",
            "as_of_date": "2026-08-12", "quote_current": True, "comparable": True,
            "exact_configuration_match": True, "currency": "CNY", "price": 100,
        }
        self.assertEqual(select_budget_anchor([item])["status"], "needs-confirmation")

    def test_duplicate_candidate_name_cannot_hide_unverified_anchor(self) -> None:
        base = {
            "candidate": "Same display name", "product_class": "fixed-sku",
            "configuration": "SKU", "source_type": "retail-exact-sku",
            "source_date": "2026-08-12", "as_of_date": "2026-08-12",
            "quote_current": True, "comparable": True, "exact_configuration_match": True,
            "currency": "CNY", "price": 50,
        }
        verified = {**base, "technical_fit_status": "PASS", "eligible_for_pricing": True, "source": "A"}
        unverified = {**base, "source": "B"}
        result = assess_budget_revision(100, [verified, unverified])
        self.assertEqual(result["decision"], "revise-to-current-anchor")
        self.assertEqual(result["budget_anchor"]["anchor_count"], 1)
        self.assertEqual(result["budget_anchor"]["excluded_signal_count"], 1)

    def test_shared_skill_requires_budget_revision_guard(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("### Mandatory existing-budget revision workflow", skill)
        self.assertIn("--existing-budget <old-unit-price>", skill)
        self.assertIn("--product-class configurable-enterprise", skill)
        self.assertIn("Partial-config + configuration-difference estimate", skill)
        self.assertIn("hold-existing-provisional", skill)
        self.assertIn("budget-revision", skill)

    def test_partial_public_context_cannot_lower_existing_server_budget(self) -> None:
        items = [
            {
                "candidate": "same-family-public-config-A",
                "product_class": "configurable-enterprise",
                "configuration": "same chassis; dual CPU; 64GB; partial SSD configuration",
                "source_type": "market-aggregator",
                "source_date": "2026-08-12",
                "quote_current": True,
                "technical_fit_status": "PASS",
                "eligible_for_pricing": True,
                "comparable": True,
                "configuration_match_score": 0.74,
                "price": 47000,
                "quote_mode": "generic-listing",
            },
            {
                "candidate": "same-family-public-config-B",
                "product_class": "configurable-enterprise",
                "configuration": "same chassis; single CPU; 32GB; 4TB storage",
                "source_type": "generic-listing",
                "source_date": "2026-08-12",
                "quote_current": True,
                "technical_fit_status": "PASS",
                "eligible_for_pricing": True,
                "comparable": True,
                "configuration_match_score": 0.71,
                "price": 16600,
            },
            {
                "candidate": "configuration-difference-estimate",
                "product_class": "configurable-enterprise",
                "configuration": SERVER_CONFIG,
                "source_type": "engineering-estimate",
                "source_date": "2026-08-12",
                "quote_current": False,
                "comparable": True,
                "configuration_match_score": 1.0,
                "price": 60000,
            },
        ]

        revision = assess_budget_revision(65000, items)
        self.assertEqual(revision["decision"], "hold-existing-provisional")
        self.assertEqual(revision["recommended_budget_low"], 65000.0)
        self.assertEqual(revision["recommended_budget_high"], 65000.0)
        self.assertEqual(revision["confidence"], "Needs confirmation")
        self.assertIn("cannot justify lowering", revision["reason"])

    def test_user_supplied_exact_quotes_are_tier_one_even_without_public_url(self) -> None:
        items = [
            {
                "candidate": "Lenovo human quote",
                "product_class": "configurable-enterprise",
                "configuration": SERVER_CONFIG,
                "source_type": "user-provided-current-quote",
                "source_date": "2026-08-12",
                "quote_current": True,
                "technical_fit_status": "PASS",
                "eligible_for_pricing": True,
                "comparable": True,
                "exact_configuration_match": True,
                "price": 89000,
                "currency": "CNY",
                "tax_included": True,
                "mandatory_accessories": 0,
                "required_licenses": 0,
                "warranty_support": 0,
                "required_implementation": 0,
                "tax_amount": 0,
                "shipping": 0,
                "orderability_confirmed": True,
                "price_scope_complete": True,
            },
            {
                "candidate": "H3C human quote",
                "product_class": "configurable-enterprise",
                "configuration": SERVER_CONFIG,
                "source_type": "project-saved-current-quote",
                "source_date": "2026-08-12",
                "quote_current": True,
                "technical_fit_status": "PASS",
                "eligible_for_pricing": True,
                "comparable": True,
                "exact_configuration_match": True,
                "price": 91500,
                "currency": "CNY",
                "tax_included": True,
                "mandatory_accessories": 0,
                "required_licenses": 0,
                "warranty_support": 0,
                "required_implementation": 0,
                "tax_amount": 0,
                "shipping": 0,
                "orderability_confirmed": True,
                "price_scope_complete": True,
            },
            {
                "candidate": "generic web listing",
                "product_class": "configurable-enterprise",
                "configuration": "same chassis, incomplete configuration",
                "source_type": "market-aggregator",
                "source_date": "2026-08-12",
                "quote_current": True,
                "comparable": True,
                "configuration_match_score": 0.72,
                "price": 46000,
            },
        ]

        anchor = select_budget_anchor(items)
        self.assertEqual(anchor["preferred_evidence_priority"], 1)
        self.assertEqual(anchor["recommended_budget_low"], 89000.0)
        self.assertEqual(anchor["recommended_budget_high"], 91500.0)
        self.assertEqual(anchor["confidence"], "Market-verified / Exact-config")

        revision = assess_budget_revision(65000, items)
        self.assertEqual(revision["decision"], "revise-to-current-anchor")
        self.assertEqual(revision["recommended_budget_low"], 89000.0)
        self.assertEqual(revision["recommended_budget_high"], 91500.0)

    def test_one_highly_matched_quote_is_not_enough_to_lower_existing_budget(self) -> None:
        items = [
            {
                "candidate": "one highly matched quote",
                "product_class": "configurable-enterprise",
                "configuration": SERVER_CONFIG,
                "source_type": "enterprise-marketplace-quote",
                "source_date": "2026-08-12",
                "quote_current": True,
                "comparable": True,
                "configuration_match_score": 0.90,
                "price": 59000,
            }
        ]

        revision = assess_budget_revision(65000, items)
        self.assertEqual(revision["decision"], "hold-existing-provisional")
        self.assertEqual(revision["recommended_budget_low"], 65000.0)
        self.assertEqual(revision["recommended_budget_high"], 65000.0)


if __name__ == "__main__":
    unittest.main()

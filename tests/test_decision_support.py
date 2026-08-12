import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DecisionSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = load_module("guide_requirements", "scripts/guide_requirements.py")
        cls.compare = load_module("compare_vendors", "scripts/compare_vendors.py")
        cls.tco = load_module("calculate_tco", "scripts/calculate_tco.py")
        cls.templates = json.loads((ROOT / "assets/scenario-templates.json").read_text(encoding="utf-8"))

    def test_scenario_template_guides_without_forcing_architecture(self):
        result = self.guide.analyze_requirements(
            "manufacturing-scada-small",
            {"scada_io_points": 3000},
            template_data=self.templates,
        )
        self.assertFalse(result["ready_for_architecture"])
        self.assertIn("historian_points", result["missing_required_fields"])
        self.assertIn("growth_margin", result["suggested_assumptions"])
        note = result["note"].lower()
        self.assertIn("must not force hci", note)
        self.assertNotIn("hci_required", result["known_fields"])

    def test_guided_questions_skip_known_fields_and_limit_length(self):
        result = self.guide.analyze_requirements(
            "smb-erp",
            {
                "erp_product_and_database": "ERP + PostgreSQL",
                "named_users": 200,
                "concurrent_users": 80,
            },
            max_questions=3,
            template_data=self.templates,
        )
        keys = [q["key"] for q in result["questions"]]
        self.assertNotIn("named_users", keys)
        self.assertLessEqual(len(keys), 3)

    def test_partial_composite_requirement_remains_unresolved(self):
        result = self.guide.analyze_requirements(
            "smb-erp",
            {
                "erp_product_and_database": "ERP + PostgreSQL",
                "named_users": 200,
                "concurrent_users": 80,
                "database_size": {"current_size": "500 GB", "annual_growth": "100 GB/year"},
                "availability_rto_rpo": {"rto": "2 hours", "rpo": "TBD"},
                "backup_retention": "30 days",
                "budget_cap": 300000,
                "domestic_xinchuang_required": False,
            },
            template_data=self.templates,
        )
        self.assertIn("availability_rto_rpo", result["missing_required_fields"])
        self.assertFalse(result["ready_for_architecture"])

    def test_unstructured_composite_answer_is_not_silently_complete(self):
        result = self.guide.analyze_requirements(
            "smb-erp",
            {
                "availability_rto_rpo": "RTO <= 2 hours",
            },
            template_data=self.templates,
        )
        self.assertIn("availability_rto_rpo", result["missing_required_fields"])

    def test_mandatory_pass_outranks_conditional_and_fail(self):
        data = {
            "constraints": [
                {
                    "key": "memory_gb",
                    "name": "Memory >= 128 GB",
                    "operator": "min",
                    "value": 128,
                    "severity": "mandatory",
                }
            ],
            "criteria": [{"key": "cost", "name": "Cost", "weight": 100}],
            "candidates": [
                {
                    "name": "PASS lower score",
                    "attributes": {"memory_gb": 128},
                    "scores": {"cost": {"score": 5, "evidence": "Verified"}},
                },
                {
                    "name": "CONDITIONAL high score",
                    "attributes": {},
                    "scores": {"cost": {"score": 10, "evidence": "Verified"}},
                },
                {
                    "name": "FAIL high score",
                    "attributes": {"memory_gb": 64},
                    "scores": {"cost": {"score": 10, "evidence": "Verified"}},
                },
            ],
        }
        ranked = self.compare.score_candidates(data)
        self.assertEqual(
            [(x["name"], x["gate"]) for x in ranked],
            [
                ("PASS lower score", "PASS"),
                ("CONDITIONAL high score", "CONDITIONAL"),
                ("FAIL high score", "FAIL"),
            ],
        )

    def test_missing_mandatory_attribute_is_conditional_not_pass(self):
        gates = self.compare.constraint_gates(
            [{"key": "warranty_years", "operator": "min", "value": 3, "severity": "mandatory"}],
            {},
        )
        self.assertEqual(self.compare.overall_gate(gates), "CONDITIONAL")

    def test_unknown_gate_status_never_becomes_pass(self):
        self.assertEqual(self.compare.overall_gate([{"status": "typo"}]), "CONDITIONAL")

    def test_unknown_mandatory_attribute_is_conditional(self):
        gates = self.compare.constraint_gates(
            [{"key": "support", "operator": "eq", "value": "active", "severity": "mandatory"}],
            {"support": "unknown"},
        )
        self.assertEqual(gates[0]["status"], "CONDITIONAL")

    def test_negative_weight_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            self.compare.score_candidates(
                {
                    "criteria": [{"key": "cost", "weight": -1}],
                    "candidates": [{"name": "A", "scores": {"cost": {"score": 9}}}],
                }
            )

    def test_string_false_is_not_treated_as_boolean_false(self):
        with self.assertRaisesRegex(ValueError, "JSON boolean"):
            self.compare.compare_value("false", "falsy", False)

    def test_tco_calculates_three_and_five_year_costs(self):
        data = {
            "electricity_rate_per_kwh": 0.8,
            "pue": 1.5,
            "years": [3, 5],
            "candidates": [
                {
                    "name": "A",
                    "purchase_cost": 100000,
                    "one_time_implementation": 10000,
                    "average_it_power_w": 1000,
                    "annual_support": 5000,
                    "annual_license": 2000,
                    "annual_facility": 0,
                    "annual_other_opex": 0,
                }
            ],
        }
        result = self.tco.calculate(data)
        self.assertEqual(len(result["results"]), 2)
        year3 = result["results"][0]
        expected_energy = 1.0 * 1.5 * 8760 * 3 * 0.8
        expected_total = 110000 + expected_energy + (7000 * 3)
        self.assertEqual(year3["status"], "complete")
        self.assertAlmostEqual(year3["energy_cost"], expected_energy, places=2)
        self.assertAlmostEqual(year3["total_tco"], expected_total, places=2)

    def test_tco_missing_costs_remain_explicit_not_zero(self):
        result = self.tco.calculate(
            {
                "electricity_rate_per_kwh": 0.8,
                "pue": 1.5,
                "years": [5],
                "candidates": [
                    {
                        "name": "Incomplete",
                        "purchase_cost": 100000,
                        "one_time_implementation": 0,
                        "average_it_power_w": 800,
                    }
                ],
            }
        )
        row = result["results"][0]
        self.assertEqual(row["status"], "incomplete-needs-confirmation")
        self.assertIsNone(row["total_tco"])
        self.assertIn("annual_support", row["missing_fields"])
        self.assertIn("annual_license", row["missing_fields"])
        self.assertGreater(row["known_cost_floor"], 100000)

    def test_tco_missing_power_is_incomplete_when_electricity_is_in_scope(self):
        result = self.tco.calculate(
            {
                "electricity_rate_per_kwh": 0.8,
                "pue": 1.5,
                "years": [3],
                "candidates": [
                    {
                        "name": "No power",
                        "purchase_cost": 100000,
                        "one_time_implementation": 0,
                        "annual_support": 0,
                        "annual_license": 0,
                        "annual_facility": 0,
                        "annual_other_opex": 0,
                    }
                ],
            }
        )
        row = result["results"][0]
        self.assertIn("average_it_power_w", row["missing_fields"])
        self.assertIsNone(row["total_tco"])

    def test_tco_requires_explicit_electricity_scope(self):
        with self.assertRaises(ValueError):
            self.tco.calculate(
                {
                    "pue": 1.5,
                    "candidates": [{"name": "A", "purchase_cost": 100000}],
                }
            )

    def test_tco_requires_pue_when_electricity_is_included(self):
        with self.assertRaises(ValueError):
            self.tco.calculate(
                {
                    "electricity_rate_per_kwh": 0.8,
                    "candidates": [{"name": "A", "purchase_cost": 100000}],
                }
            )


if __name__ == "__main__":
    unittest.main()

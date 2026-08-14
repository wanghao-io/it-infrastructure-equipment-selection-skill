from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "SKILL.md"
README_PATH = ROOT / "README.md"


class SkillRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")

    def test_router_has_deliberate_progressive_disclosure_size(self) -> None:
        lines = self.skill.splitlines()
        self.assertGreaterEqual(len(lines), 180)
        self.assertLessEqual(len(lines), 300)
        self.assertIn("This file is the workflow router and invariant set", self.skill)

    def test_exactly_twelve_stable_invariants_are_present(self) -> None:
        expected = [
            "INV-REQ-FIRST",
            "INV-UNKNOWN-EXPLICIT",
            "INV-NO-DEFAULT-ARCH",
            "INV-MANDATORY-BEFORE-SCORE",
            "INV-TECH-BEFORE-PRICE",
            "INV-LIVE-PRICE",
            "INV-EXACT-CONFIG",
            "INV-BUDGET-REVISION",
            "INV-OT-AUTHORITY",
            "INV-SCHEMA-NOT-TRUTH",
            "INV-PRIVATE-BOUNDARY",
            "INV-RISK-DISCLOSURE",
        ]
        found = re.findall(r"\bINV-[A-Z-]+\b", self.skill)
        self.assertEqual(found, expected)

    def test_all_supported_task_modes_are_discoverable(self) -> None:
        modes = {
            "guided-requirements",
            "project-design",
            "single-device",
            "alternative-search",
            "price-research",
            "budget-revision",
            "server-rfq",
            "vendor-compare",
            "tco-analysis",
            "bom-budget",
            "tender-spec",
            "compliance-check",
            "topology-generation",
            "reference-design",
            "schema-migration",
            "private-extension",
        }
        for mode in sorted(modes):
            with self.subTest(mode=mode):
                self.assertIn(mode, self.skill)

    def test_every_reference_is_reachable_from_the_router(self) -> None:
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "references").glob("*.md")
            if path.is_file()
        }
        routed = set(re.findall(r"references/[A-Za-z0-9_.-]+\.md", self.skill))
        self.assertEqual(routed, expected)

    def test_every_non_internal_catalog_script_is_reachable(self) -> None:
        catalog = json.loads((ROOT / "assets/tool-catalog.json").read_text(encoding="utf-8"))
        expected = {
            item["script"]
            for item in catalog["tools"].values()
            if item.get("exposure") != "internal"
        }
        routed = set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", self.skill))
        self.assertTrue(expected.issubset(routed), sorted(expected - routed))

    def test_router_paths_exist_and_are_portable(self) -> None:
        paths = set(re.findall(
            r"(?:references|scripts|assets|schemas)/[A-Za-z0-9_./-]+(?:\.md|\.py|\.json|\.csv)",
            self.skill,
        ))
        self.assertTrue(paths)
        for relative in sorted(paths):
            with self.subTest(path=relative):
                self.assertNotIn("\\", relative)
                self.assertFalse(Path(relative).is_absolute())
                self.assertTrue((ROOT / relative).is_file())

    def test_high_risk_routes_and_fallbacks_remain_explicit(self) -> None:
        required_fragments = [
            "## Routing precedence",
            "## Capability fallbacks",
            "## High-risk route checks",
            "references/budget-revision.md",
            "references/ot-control-safety.md",
            "references/private-extensions.md",
            "revise-to-current-anchor",
            "eligible_for_pricing=true",
            "Needs confirmation",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.skill)

    def test_minimum_output_contract_covers_each_project_stage(self) -> None:
        self.assertIn("## Output contract", self.skill)
        self.assertIn("## Minimum deliverables by stage", self.skill)
        for profile in (
            "quick-selection",
            "internal-review",
            "procurement-rfq",
            "detailed-design",
            "compliance-check",
            "bom-budget",
            "budget-revision",
        ):
            self.assertIn(profile, self.skill)


class RoutedReferenceTests(unittest.TestCase):
    def test_budget_revision_reference_contains_complete_mandatory_workflow(self) -> None:
        reference = (ROOT / "references/budget-revision.md").read_text(encoding="utf-8")
        workflow = reference.split("## Mandatory workflow", 1)[1].split("## Universal technical-fit gate", 1)[0]
        steps = [int(value) for value in re.findall(r"^(\d+)\. ", workflow, re.MULTILINE)]
        self.assertEqual(steps, list(range(1, 13)))
        for fragment in (
            "revision baseline",
            "technical_fit_status = PASS",
            "eligible_for_pricing = true",
            "Tier-1 or Tier-2",
            "two supplier-independent Tier-3",
            "Partial-config + configuration-difference estimate",
            "hold-existing-provisional",
            "revise-to-current-anchor",
            "decision_scope_id",
        ):
            self.assertIn(fragment, reference)

    def test_price_evidence_reference_documents_current_v2_semantics(self) -> None:
        reference = (ROOT / "references/price-evidence.md").read_text(encoding="utf-8")
        for fragment in (
            "schemas/v2/price-evidence.schema.json",
            '"schema_version": 2',
            '"decision_scope_id"',
            "declared_evidence_level",
            "derived_evidence_level",
            "supplier/channel",
            "newest eligible record",
            "--strict-contract",
            "references/budget-revision.md",
        ):
            self.assertIn(fragment, reference)

    def test_bom_reference_preserves_commercial_claim_boundary(self) -> None:
        reference = (ROOT / "references/bom-checklist.md").read_text(encoding="utf-8")
        self.assertIn("## Commercial Claim Boundary", reference)
        for phrase in ("tax included", "delivered", "fully scoped", "TBD", "Needs confirmation"):
            self.assertIn(phrase, reference)


class ReadmeCurrentStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = README_PATH.read_text(encoding="utf-8")

    def test_readme_exposes_two_paths_and_copyable_recipes(self) -> None:
        for heading in (
            "## 两条使用路径",
            "### 路径 A：Agent 完整工作流",
            "### 路径 B：确定性 CLI 与 Schema",
            "## 可复制任务配方",
            "## Schema v1 / v2 治理",
            "## 私有扩展边界",
            "## 测试与社区",
        ):
            self.assertIn(heading, self.readme)
        self.assertIn("$it-infrastructure-equipment-selection", self.readme)
        self.assertIn("scripts/infra_cli.py list", self.readme)

    def test_readme_describes_current_contract_and_safety_features(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(f"Current stable version: **v{version}**", self.readme)
        for fragment in (
            "price-evidence-v2",
            "scripts/migrate_schema.py",
            "decision_scope_id",
            "供应商独立性",
            "hci-failover",
            "private-extension-manifest-v1",
            "references/budget-revision.md",
            "docs/forward-validation-v1.4.2.md",
        ):
            self.assertIn(fragment, self.readme)
        self.assertNotIn("当前公开的两份脱敏案例", self.readme)
        self.assertNotRegex(self.readme, r"(?m)^## v1\.[0-9]+")

    def test_all_local_markdown_links_resolve(self) -> None:
        targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", self.readme)
        for target in targets:
            if target.startswith(("http://", "https://", "#")) or target.startswith("../../"):
                continue
            path_text = target.split("#", 1)[0]
            if not path_text:
                continue
            with self.subTest(target=target):
                self.assertTrue((ROOT / path_text).exists())


if __name__ == "__main__":
    unittest.main()

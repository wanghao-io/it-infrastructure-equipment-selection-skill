from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommunityHealthTests(unittest.TestCase):
    def test_required_community_entry_points_exist(self) -> None:
        required = (
            "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "SUPPORT.md",
            "GOVERNANCE.md", "MAINTAINERS.md", ".github/CODEOWNERS",
            ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/config.yml",
            ".github/ISSUE_TEMPLATE/bug.yml", ".github/ISSUE_TEMPLATE/feature.yml",
            ".github/ISSUE_TEMPLATE/documentation.yml", "docs/maintainer-release-runbook.md",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_contributing_is_actionable(self) -> None:
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertGreater(len(text), 2500)
        for marker in (
            "GitHub Discussions", "python3 -m unittest discover", "Pull requests",
            "GOVERNANCE.md", "maintainer-release-runbook.md",
        ):
            self.assertIn(marker, text)

    def test_governance_does_not_overstate_bus_factor(self) -> None:
        governance = (ROOT / "GOVERNANCE.md").read_text(encoding="utf-8")
        maintainers = (ROOT / "MAINTAINERS.md").read_text(encoding="utf-8")
        self.assertIn("bus factor is therefore **1**", governance)
        self.assertIn("two active humans", governance)
        self.assertIn("Current human bus factor: **1**", maintainers)
        self.assertIn("Release maintainer | 1+", maintainers)

    def test_security_uses_private_reporting_not_private_discussion(self) -> None:
        text = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("security/advisories/new", text)
        self.assertNotIn("private discussion", text.lower())

    def test_issue_and_support_routes_are_real(self) -> None:
        config = (ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
        support = (ROOT / "SUPPORT.md").read_text(encoding="utf-8")
        self.assertIn("blank_issues_enabled: false", config)
        self.assertIn("/discussions", config)
        self.assertIn("security/advisories/new", config)
        self.assertIn("bug.yml", support)
        self.assertIn("feature.yml", support)
        self.assertIn("documentation.yml", support)

    def test_release_runbook_covers_build_publish_and_recovery(self) -> None:
        text = (ROOT / "docs/maintainer-release-runbook.md").read_text(encoding="utf-8")
        for marker in (
            "python3 scripts/validate_release.py", "git tag -a", "git push origin",
            "gh run watch", "skill.tar.gz", "SHA256SUMS", "Failure and recovery",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()

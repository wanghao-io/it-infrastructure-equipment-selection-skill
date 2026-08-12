#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from install_skill import (  # noqa: E402
    RUNTIME_ENTRIES,
    SKILL_NAME,
    install_skill,
    resolve_destination,
)


class AgentSkillMetadataTests(unittest.TestCase):
    def test_portable_frontmatter(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]

        name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        description_match = re.search(
            r"^description:\s*>\s*\n(?P<body>(?:^[ ]{2}.+\n?)+)",
            frontmatter,
            re.MULTILINE,
        )
        license_match = re.search(r"^license:\s*(.+)$", frontmatter, re.MULTILINE)

        self.assertIsNotNone(name_match)
        self.assertIsNotNone(description_match)
        self.assertIsNotNone(license_match)

        name = name_match.group(1).strip()
        description = " ".join(
            line.strip() for line in description_match.group("body").splitlines()
        )

        self.assertEqual(name, SKILL_NAME)
        self.assertRegex(name, r"^[a-z0-9-]+$")
        self.assertLessEqual(len(name), 64)
        self.assertGreater(len(description), 0)
        self.assertLessEqual(len(description), 1024)
        self.assertEqual(license_match.group(1).strip(), "MIT")

    def test_openai_metadata_is_optional_extension(self) -> None:
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertIn("SKILL.md", RUNTIME_ENTRIES)
        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("interface:", metadata)
        self.assertIn("$it-infrastructure-equipment-selection", metadata)


class InstallationPathTests(unittest.TestCase):
    def test_user_paths(self) -> None:
        home = Path("/tmp/example-home").resolve()
        self.assertEqual(
            resolve_destination("codex", "user", home=home),
            home / ".agents" / "skills" / SKILL_NAME,
        )
        self.assertEqual(
            resolve_destination("claude-code", "user", home=home),
            home / ".claude" / "skills" / SKILL_NAME,
        )
        self.assertEqual(
            resolve_destination("copilot", "user", home=home),
            home / ".agents" / "skills" / SKILL_NAME,
        )
        self.assertEqual(
            resolve_destination("gemini", "user", home=home),
            home / ".agents" / "skills" / SKILL_NAME,
        )

    def test_project_paths(self) -> None:
        project = Path("/tmp/example-project").resolve()
        self.assertEqual(
            resolve_destination("codex", "project", project_dir=project),
            project / ".agents" / "skills" / SKILL_NAME,
        )
        self.assertEqual(
            resolve_destination("claude-code", "project", project_dir=project),
            project / ".claude" / "skills" / SKILL_NAME,
        )
        self.assertEqual(
            resolve_destination("copilot", "project", project_dir=project),
            project / ".github" / "skills" / SKILL_NAME,
        )
        self.assertEqual(
            resolve_destination("gemini", "project", project_dir=project),
            project / ".agents" / "skills" / SKILL_NAME,
        )

    def test_copy_install_contains_portable_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / ".claude" / "skills" / SKILL_NAME
            installed = install_skill(ROOT, destination, mode="copy")

            self.assertEqual(installed, destination)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertEqual(
                (destination / "VERSION").read_text(encoding="utf-8").strip(),
                (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            )
            self.assertTrue((destination / "references").is_dir())
            self.assertTrue((destination / "scripts").is_dir())
            self.assertTrue((destination / "assets").is_dir())
            self.assertTrue((destination / "examples").is_dir())
            self.assertTrue((destination / "agents" / "openai.yaml").is_file())
            self.assertFalse((destination / ".git").exists())
            self.assertFalse((destination / "tests").exists())

    def test_aliases(self) -> None:
        home = Path("/tmp/example-home").resolve()
        self.assertEqual(
            resolve_destination("claude", "user", home=home),
            resolve_destination("claude-code", "user", home=home),
        )
        self.assertEqual(
            resolve_destination("github-copilot", "user", home=home),
            resolve_destination("copilot", "user", home=home),
        )
        self.assertEqual(
            resolve_destination("gemini-cli", "user", home=home),
            resolve_destination("gemini", "user", home=home),
        )


if __name__ == "__main__":
    unittest.main()

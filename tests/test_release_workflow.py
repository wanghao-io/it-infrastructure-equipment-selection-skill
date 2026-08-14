from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_release_notes import ReleaseNotesError, extract_release_notes  # noqa: E402
from validate_release import validate  # noqa: E402


def job_block(workflow: str, name: str) -> str:
    match = re.search(
        rf"^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [a-z][a-z0-9-]*:\n|\Z)",
        workflow,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"workflow job not found: {name}")
    return match.group("body")


class ReleaseNotesExtractionTests(unittest.TestCase):
    def test_extracts_only_requested_version(self) -> None:
        changelog = """# Changelog

## v2.0.0 — 2026-08-15

### Added

- Current release.

## v1.9.0 — 2026-08-14

- Previous release.
"""
        notes = extract_release_notes(changelog, "v2.0.0")
        self.assertIn("Current release", notes)
        self.assertNotIn("v1.9.0", notes)
        self.assertNotIn("Previous release", notes)

    def test_duplicate_or_missing_section_is_rejected(self) -> None:
        duplicate = """## v2.0.0

- First.

## v2.0.0

- Duplicate.
"""
        with self.assertRaisesRegex(ReleaseNotesError, "found 2"):
            extract_release_notes(duplicate, "2.0.0")
        with self.assertRaisesRegex(ReleaseNotesError, "found 0"):
            extract_release_notes(duplicate, "2.1.0")

    def test_empty_release_section_is_rejected(self) -> None:
        with self.assertRaisesRegex(ReleaseNotesError, "no release content"):
            extract_release_notes("## v2.0.0\n\n### Added\n\n## v1.9.0\n\n- Older.\n", "2.0.0")

    def test_section_stops_at_any_next_level_two_heading(self) -> None:
        changelog = """## v2.0.0

- Current.

## Unreleased notes

- Not part of v2.0.0.
"""
        notes = extract_release_notes(changelog, "2.0.0")
        self.assertIn("Current", notes)
        self.assertNotIn("Unreleased", notes)
        self.assertNotIn("Not part", notes)

    def test_repository_current_version_has_one_isolated_section(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        notes = extract_release_notes((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version)
        self.assertTrue(notes.startswith(f"## v{version}"))
        headings = re.findall(r"^## v\d+\.\d+\.\d+", notes, flags=re.MULTILINE)
        self.assertEqual(headings, [f"## v{version}"])
        self.assertEqual(validate(ROOT), [])

        release_notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        self.assertTrue(release_notes.startswith(f"# IT Infrastructure Equipment Selection Skill v{version}\n"))
        self.assertEqual(
            re.findall(
                r"^# IT Infrastructure Equipment Selection Skill v\d+\.\d+\.\d+$",
                release_notes,
                flags=re.MULTILINE,
            ),
            [f"# IT Infrastructure Equipment Selection Skill v{version}"],
        )
        self.assertNotRegex(release_notes, r"(?m)^## v\d+\.\d+\.\d+\b")


class ReleaseWorkflowStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validation = (ROOT / ".github/workflows/validate-skill.yml").read_text(encoding="utf-8")
        cls.release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

    def test_validation_workflow_is_reusable_without_losing_existing_gates(self) -> None:
        for marker in (
            "workflow_call:",
            "push:",
            "pull_request:",
            "os: [ubuntu-latest, macos-latest, windows-latest]",
            "python-version: ['3.10', '3.12']",
            "python -m compileall scripts tests",
            "python scripts/validate_release.py",
            "python scripts/validate_json_schemas.py --catalog",
            "python -m unittest discover",
            "Deterministic workflow smoke tests",
            "package-smoke:",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.validation)

    def test_release_reuses_full_validation_before_build(self) -> None:
        self.assertIn("uses: ./.github/workflows/validate-skill.yml", self.release)
        build = job_block(self.release, "build-release")
        self.assertIn("needs: [metadata-gate, full-validation, gh-skill-dry-run]", build)
        self.assertIn("Smoke test the clean release archive", build)
        self.assertIn("tar -xzf \"$RUNNER_TEMP/skill.tar.gz\"", build)
        self.assertIn("scripts/install_skill.py", build)

    def test_tag_must_match_version_and_exact_main_head(self) -> None:
        metadata = job_block(self.release, "metadata-gate")
        self.assertIn('test "$TAG" = "v$(cat VERSION)"', metadata)
        self.assertIn("^v[0-9]+\\.[0-9]+\\.[0-9]+$", metadata)
        self.assertIn("git fetch --no-tags origin main:refs/remotes/origin/main", metadata)
        self.assertIn('test "$GITHUB_SHA" = "$(git rev-parse origin/main)"', metadata)
        self.assertNotIn("merge-base --is-ancestor", metadata)

    def test_runner_gh_is_feature_gated_before_ephemeral_dry_run(self) -> None:
        dry_run = job_block(self.release, "gh-skill-dry-run")
        self.assertIn("Verify runner gh skill publish compatibility", dry_run)
        self.assertIn('PUBLISH_ROOT="$RUNNER_TEMP/gh-skill-publish"', dry_run)
        self.assertIn("/it-infrastructure-equipment-selection\"", dry_run)
        self.assertIn('git archive "$GITHUB_SHA"', dry_run)
        self.assertIn("gh --version", dry_run)
        self.assertIn("gh skill publish --help", dry_run)
        self.assertIn("does not provide the required 'skill publish' command", dry_run)
        self.assertIn("does not provide the required --dry-run flag", dry_run)
        self.assertIn('gh skill publish "$PUBLISH_ROOT" --dry-run', dry_run)
        self.assertNotIn("continue-on-error", dry_run)
        self.assertNotIn("|| true", dry_run)
        self.assertNotRegex(dry_run, r"gh skill publish[^\n]*(?:--fix|--tag(?:\s|$))")

    def test_publish_is_single_writer_least_privilege_and_non_clobbering(self) -> None:
        publish = job_block(self.release, "publish-release")
        self.assertEqual(self.release.count("contents: write"), 1)
        self.assertIn("contents: read", self.release)
        self.assertIn("group: release-publish", self.release)
        self.assertIn("cancel-in-progress: false", self.release)
        self.assertIn("environment: release", publish)
        self.assertIn("needs: build-release", publish)
        self.assertEqual(self.release.count("gh release create"), 1)
        self.assertIn("--verify-tag", publish)
        self.assertIn('gh api "repos/$GITHUB_REPOSITORY/git/ref/heads/main"', publish)
        self.assertIn('if [ "$GITHUB_SHA" != "$CURRENT_MAIN_SHA" ]', publish)
        self.assertIn("already exists; refusing to overwrite", publish)
        self.assertNotIn("--clobber", self.release)
        self.assertNotIn("actions/checkout", publish)

    def test_release_body_comes_from_single_changelog_section(self) -> None:
        self.assertIn("scripts/extract_release_notes.py", self.release)
        self.assertIn("--notes-file release-notes.md", self.release)
        self.assertNotIn("--notes-file RELEASE_NOTES.md", self.release)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from install_skill import install_skill  # noqa: E402


class InstallerUpdateTests(unittest.TestCase):
    def _make_source(self, root: Path, text: str = "new") -> Path:
        source = root / "source"
        (source / "references").mkdir(parents=True)
        (source / "SKILL.md").write_text(f"# {text}\n", encoding="utf-8")
        (source / "references" / "example.md").write_text(text, encoding="utf-8")
        return source

    def test_copy_installation_cannot_destructively_update_itself(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            source = self._make_source(Path(td))
            before = (source / "SKILL.md").read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "independent clone"):
                install_skill(source, source, update=True)
            self.assertEqual((source / "SKILL.md").read_text(encoding="utf-8"), before)

    def test_copy_update_preserves_unmanaged_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self._make_source(root)
            destination = root / "installed"
            (destination / "references").mkdir(parents=True)
            (destination / "SKILL.md").write_text("# old\n", encoding="utf-8")
            (destination / "references" / "example.md").write_text("old", encoding="utf-8")
            (destination / "local-notes.txt").write_text("keep me", encoding="utf-8")

            install_skill(source, destination, update=True)

            self.assertEqual((destination / "SKILL.md").read_text(encoding="utf-8"), "# new\n")
            self.assertEqual(
                (destination / "references" / "example.md").read_text(encoding="utf-8"),
                "new",
            )
            self.assertEqual(
                (destination / "local-notes.txt").read_text(encoding="utf-8"),
                "keep me",
            )

    def test_force_never_deletes_git_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self._make_source(root)
            destination = root / "installed"
            (destination / ".git").mkdir(parents=True)
            (destination / "SKILL.md").write_text("# old\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Refusing to delete .git"):
                install_skill(source, destination, force=True)

            self.assertTrue((destination / ".git").exists())
            self.assertEqual((destination / "SKILL.md").read_text(encoding="utf-8"), "# old\n")

    def test_git_installation_fast_forwards_and_refuses_dirty_tree(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            remote = root / "remote.git"
            publisher = root / "publisher"
            installed = root / "installed"

            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            subprocess.run(["git", "clone", str(remote), str(publisher)], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(publisher), "config", "user.email", "ci@example.invalid"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(publisher), "config", "user.name", "CI"],
                check=True,
            )
            (publisher / "SKILL.md").write_text(
                "---\nname: it-infrastructure-equipment-selection\ndescription: test\n---\n# v1\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(publisher), "add", "SKILL.md"], check=True)
            subprocess.run(["git", "-C", str(publisher), "commit", "-m", "v1"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(publisher), "push", "origin", "HEAD"], check=True, capture_output=True)

            subprocess.run(["git", "clone", str(remote), str(installed)], check=True, capture_output=True)

            (publisher / "SKILL.md").write_text(
                "---\nname: it-infrastructure-equipment-selection\ndescription: test\n---\n# v2\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(publisher), "add", "SKILL.md"], check=True)
            subprocess.run(["git", "-C", str(publisher), "commit", "-m", "v2"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(publisher), "push", "origin", "HEAD"], check=True, capture_output=True)

            install_skill(publisher, installed, update=True)
            self.assertIn("# v2", (installed / "SKILL.md").read_text(encoding="utf-8"))

            (installed / "local.txt").write_text("local change", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "local changes"):
                install_skill(publisher, installed, update=True)

    def test_update_rejects_unrelated_git_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "unrelated"
            target.mkdir()
            subprocess.run(["git", "init", str(target)], check=True, capture_output=True)
            (target / "SKILL.md").write_text("# another project\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "is not it-infrastructure"):
                install_skill(target, target, update=True)


if __name__ == "__main__":
    unittest.main()

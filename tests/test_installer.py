#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from install_skill import install_skill  # noqa: E402


class InstallerUpdateTests(unittest.TestCase):
    def _make_source(self, root: Path, text: str = "new") -> Path:
        source = root / "source"
        install_skill(ROOT, source)
        with (source / "SKILL.md").open("a", encoding="utf-8") as handle:
            handle.write(f"# {text}\n")
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
            install_skill(source, destination)
            (source / "references" / "example.md").write_text("new", encoding="utf-8")
            (destination / "local-notes.txt").write_text("keep me", encoding="utf-8")

            install_skill(source, destination, update=True)

            self.assertIn("# new\n", (destination / "SKILL.md").read_text(encoding="utf-8"))
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

    def test_copy_failure_preserves_complete_old_installation(self):
        import shutil
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self._make_source(root)
            destination = root / "installed"
            install_skill(source, destination)
            before = (destination / "references/example.md").read_bytes()
            (source / "references/example.md").write_text("changed", encoding="utf-8")
            original = shutil.copy2
            def fail(src, dst, *args, **kwargs):
                if Path(src).resolve() == (source / "VERSION").resolve():
                    raise OSError("injected copy failure")
                return original(src, dst, *args, **kwargs)
            with patch("install_skill.shutil.copy2", side_effect=fail):
                with self.assertRaisesRegex(OSError, "injected"):
                    install_skill(source, destination, update=True)
            self.assertEqual((destination / "references/example.md").read_bytes(), before)
            self.assertTrue((destination / "scripts/infra_cli.py").is_file())

    def test_copy_refuses_modified_managed_files(self):
        with tempfile.TemporaryDirectory() as td:
            source = self._make_source(Path(td))
            destination = Path(td) / "installed"
            install_skill(source, destination)
            (destination / "references/example.md").write_text("user edit", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "local changes"):
                install_skill(source, destination, update=True)

    def test_copy_swap_failure_rolls_back(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            source = self._make_source(Path(td))
            destination = Path(td) / "installed"
            install_skill(source, destination)
            before = (destination / "references/example.md").read_bytes()
            (source / "references/example.md").write_text("replacement", encoding="utf-8")
            original = os.replace
            def fail(src, dst):
                if Path(src).name == "staged":
                    raise OSError("injected swap failure")
                return original(src, dst)
            with patch("install_skill.os.replace", side_effect=fail):
                with self.assertRaisesRegex(OSError, "injected"):
                    install_skill(source, destination, update=True)
            self.assertEqual((destination / "references/example.md").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()

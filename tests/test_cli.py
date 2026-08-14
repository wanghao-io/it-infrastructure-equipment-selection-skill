from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/infra_cli.py"


class InfrastructureCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True)

    def test_list_and_example_are_discoverable(self) -> None:
        listed = self.run_cli("list", "--json")
        self.assertEqual(listed.returncode, 0)
        catalog = json.loads(listed.stdout)
        self.assertIn("storage", catalog["tools"])
        self.assertIn("price-evidence-v2", catalog["contracts"])
        example = self.run_cli("example", "ups")
        self.assertEqual(example.returncode, 0)
        self.assertIn("infra_cli.py run ups", example.stdout)

    def test_wrapper_matches_direct_calculator_output(self) -> None:
        direct = subprocess.run([
            sys.executable, str(ROOT / "scripts/calculate_storage.py"),
            "--drives", "6", "--drive-tb", "4", "--raid", "10",
        ], cwd=ROOT, text=True, capture_output=True)
        wrapped = self.run_cli("run", "storage", "--", "--drives", "6", "--drive-tb", "4", "--raid", "10")
        self.assertEqual(wrapped.returncode, 0)
        self.assertEqual(wrapped.stdout, direct.stdout)

    def test_invalid_tool_input_has_no_wrapper_traceback(self) -> None:
        result = self.run_cli("run", "storage", "--", "--drives", "0", "--drive-tb", "4", "--raid", "10")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("drive_count and drive_tb must be > 0", result.stderr)

    def test_named_contract_validation(self) -> None:
        result = self.run_cli("validate", "price-evidence-v2", "assets/price-evidence-v2-example.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validation passed", result.stdout)

    def test_migration_is_non_destructive_and_validates_v2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            fixture = json.loads((ROOT / "assets/price-evidence-example.json").read_text(encoding="utf-8"))
            fixture["items"] = fixture["items"][:1]
            source.write_text(json.dumps(fixture), encoding="utf-8")
            before = source.read_bytes()
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/migrate_schema.py"), "price-evidence", str(source),
                "--decision-scope-id", "test:bom-server-1",
            ], cwd=ROOT, text=True, capture_output=True)
            after = source.read_bytes()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)
        report = json.loads(result.stdout)
        self.assertTrue(report["source_unchanged"])
        self.assertEqual(report["result"]["schema_version"], 2)

    def test_public_assets_do_not_contain_private_overlay(self) -> None:
        paths = [path.as_posix() for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
        self.assertFalse(any("/.private/" in path or "/private-data/" in path for path in paths))
        reference = (ROOT / "references/private-extensions.md").read_text(encoding="utf-8")
        self.assertIn("Do not scan", reference)
        self.assertIn("Strip or reject supplier-supplied decision fields", reference)

    def test_skill_stays_below_progressive_disclosure_limit(self) -> None:
        self.assertLess(len((ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()), 500)


if __name__ == "__main__":
    unittest.main()

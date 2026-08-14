from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/infra_cli.py"
PUBLIC_RUN_TOOLS = {
    "storage",
    "ups",
    "historian",
    "network-ports",
    "tco",
    "hci-failover",
}
REQUIRED_CATALOG_FIELDS = {
    "script",
    "description",
    "exposure",
    "side_effects",
    "input_contract",
    "applicability",
    "limitations",
    "excluded_reason",
}


class InfrastructureCliTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=cwd or ROOT,
            text=True,
            capture_output=True,
        )

    def test_list_defaults_to_public_run_and_all_catalogues_every_script(self) -> None:
        listed = self.run_cli("list", "--json")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        available = json.loads(listed.stdout)
        self.assertEqual(set(available["tools"]), PUBLIC_RUN_TOOLS)
        self.assertIn("price-evidence-v2", available["contracts"])

        listed_all = self.run_cli("list", "--all", "--json")
        self.assertEqual(listed_all.returncode, 0, listed_all.stderr)
        complete = json.loads(listed_all.stdout)
        expected_scripts = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "scripts").glob("*.py")
            if path.is_file()
        }
        catalog_scripts = {item["script"] for item in complete["tools"].values()}
        self.assertEqual(catalog_scripts, expected_scripts)
        self.assertEqual(len(catalog_scripts), len(complete["tools"]))
        for name, item in complete["tools"].items():
            self.assertTrue(REQUIRED_CATALOG_FIELDS.issubset(item), name)
            self.assertIsInstance(item["limitations"], list, name)
            if item["exposure"] == "public-run":
                self.assertIsNone(item["excluded_reason"], name)
            else:
                self.assertTrue(item["excluded_reason"], name)

        listed_all_text = self.run_cli("list", "--all")
        self.assertEqual(listed_all_text.returncode, 0, listed_all_text.stderr)
        self.assertIn("budget-sum", listed_all_text.stdout)
        self.assertIn("excluded from run:", listed_all_text.stdout)
        listed_text = self.run_cli("list")
        self.assertNotIn("budget-sum", listed_text.stdout)

    def test_example_is_cwd_independent_and_supports_json_argv(self) -> None:
        example = self.run_cli("example", "tco", "--json")
        self.assertEqual(example.returncode, 0, example.stderr)
        argv = json.loads(example.stdout)
        self.assertEqual(argv[0], sys.executable)
        self.assertEqual(Path(argv[1]), CLI)
        self.assertTrue(Path(argv[5]).is_absolute())
        with tempfile.TemporaryDirectory() as directory:
            executed = subprocess.run(argv, cwd=directory, text=True, capture_output=True)
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.assertIn("# Infrastructure TCO", executed.stdout)

        text_example = self.run_cli("example", "ups")
        self.assertEqual(text_example.returncode, 0, text_example.stderr)
        self.assertIn(str(CLI), text_example.stdout)
        self.assertIn("run ups", text_example.stdout)

    def test_wrapper_matches_all_six_direct_calculator_outputs(self) -> None:
        cases = [
            (
                "storage",
                "calculate_storage.py",
                ["--drives", "6", "--drive-tb", "4", "--raid", "10"],
            ),
            ("ups", "calculate_ups.py", ["800", "--runtime-minutes", "10"]),
            ("historian", "calculate_historian.py", ["5000", "5", "--retention-days", "365"]),
            ("network-ports", "calculate_network_ports.py", ["80", "--uplinks", "2", "--spare-ratio", "0.25"]),
            ("tco", "calculate_tco.py", [str(ROOT / "assets/tco-example.json"), "--pretty"]),
            ("hci-failover", "calculate_hci_failover.py", [str(ROOT / "assets/hci-failover-example.json"), "--pretty"]),
        ]
        for tool, script, tool_args in cases:
            with self.subTest(tool=tool):
                direct = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / script), *tool_args],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                wrapped = self.run_cli("run", tool, "--", *tool_args)
                self.assertEqual(direct.returncode, 0, direct.stderr)
                self.assertEqual(wrapped.returncode, 0, wrapped.stderr)
                self.assertEqual(wrapped.stdout, direct.stdout)

    def test_relative_structured_inputs_resolve_from_caller_cwd(self) -> None:
        fixtures = {
            "tco": "tco-example.json",
            "hci-failover": "hci-failover-example.json",
        }
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            for tool, fixture_name in fixtures.items():
                with self.subTest(tool=tool):
                    target = cwd / fixture_name
                    target.write_bytes((ROOT / "assets" / fixture_name).read_bytes())
                    tool_args = (
                        ["--format", "json", target.name, "--pretty"]
                        if tool == "tco"
                        else ["--pretty", target.name]
                    )
                    result = self.run_cli("run", tool, "--", *tool_args, cwd=cwd)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(json.loads(result.stdout))

    def test_structured_preflight_failure_has_no_calculation_output_or_traceback(self) -> None:
        fixtures = {
            "tco": "tco-example.json",
            "hci-failover": "hci-failover-example.json",
        }
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            for tool, fixture_name in fixtures.items():
                with self.subTest(tool=tool):
                    data = json.loads((ROOT / "assets" / fixture_name).read_text(encoding="utf-8"))
                    data["unexpected_cli_field"] = True
                    target = cwd / fixture_name
                    target.write_text(json.dumps(data), encoding="utf-8")
                    result = self.run_cli("run", tool, "--", target.name, "--pretty", cwd=cwd)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn("additional property not allowed", result.stderr)

    def test_invalid_tool_input_is_concise_but_debug_preserves_traceback(self) -> None:
        arguments = ["--drives", "0", "--drive-tb", "4", "--raid", "10"]
        result = self.run_cli("run", "storage", "--", *arguments)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("drive_count and drive_tb must be > 0", result.stderr)

        debug = self.run_cli("run", "--debug", "storage", "--", *arguments)
        self.assertNotEqual(debug.returncode, 0)
        self.assertIn("Traceback (most recent call last):", debug.stderr)

    def test_run_rejects_every_non_public_exposure(self) -> None:
        catalog = json.loads(self.run_cli("list", "--all", "--json").stdout)
        for name, item in catalog["tools"].items():
            if item["exposure"] == "public-run":
                continue
            with self.subTest(tool=name):
                result = self.run_cli("run", name)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("is not available through run", result.stderr)
                self.assertIn(item["excluded_reason"], result.stderr)

    def test_named_contract_validation_uses_caller_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            target = cwd / "price-evidence.json"
            target.write_bytes((ROOT / "assets/price-evidence-v2-example.json").read_bytes())
            result = self.run_cli("validate", "price-evidence-v2", target.name, cwd=cwd)
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
        lines = (ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lines), 180)
        self.assertLessEqual(len(lines), 300)


if __name__ == "__main__":
    unittest.main()

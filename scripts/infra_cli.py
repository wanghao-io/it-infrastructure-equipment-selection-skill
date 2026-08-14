#!/usr/bin/env python3
"""Thin, safe entry point for deterministic Skill tools and contracts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "assets/tool-catalog.json"


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def resolve_catalog_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if ROOT not in path.parents:
        raise ValueError("catalog path escapes the Skill root")
    return path


def run_checked(command: list[str]) -> int:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        if "Traceback (most recent call last):" in result.stderr:
            last_line = next((line for line in reversed(result.stderr.splitlines()) if line.strip()), "tool failed")
            sys.stderr.write(f"error: {last_line}\n")
        else:
            sys.stderr.write(result.stderr)
    return result.returncode


def main() -> None:
    catalog = load_catalog()
    parser = argparse.ArgumentParser(
        description="Discover and run deterministic infrastructure calculators; Agent research remains outside this CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List supported deterministic tools and contracts")
    list_parser.add_argument("--json", action="store_true")
    example_parser = subparsers.add_parser("example", help="Show a copyable example for one tool")
    example_parser.add_argument("tool", choices=sorted(catalog["tools"]))
    validate_parser = subparsers.add_parser("validate", help="Validate a JSON file against a named contract")
    validate_parser.add_argument("contract", choices=sorted(catalog["contracts"]))
    validate_parser.add_argument("input", type=Path)
    run_parser = subparsers.add_parser("run", help="Run a whitelisted deterministic tool")
    run_parser.add_argument("tool", choices=sorted(catalog["tools"]))
    run_parser.add_argument("tool_args", nargs=argparse.REMAINDER, help="arguments passed to the selected tool")
    args = parser.parse_args()

    if args.command == "list":
        if args.json:
            print(json.dumps(catalog, ensure_ascii=False, indent=2))
        else:
            for name, item in catalog["tools"].items():
                print(f"{name:16} {item['description']}")
            print("\nContracts:")
            for name in catalog["contracts"]:
                print(f"  {name}")
        return
    if args.command == "example":
        item = catalog["tools"][args.tool]
        quoted = " ".join(json.dumps(str(value)) for value in item["example"])
        print(f"python3 scripts/infra_cli.py run {args.tool} -- {quoted}")
        return
    if args.command == "validate":
        schema = resolve_catalog_path(catalog["contracts"][args.contract])
        raise SystemExit(run_checked([
            sys.executable, str(ROOT / "scripts/validate_json_schemas.py"),
            str(args.input.resolve()), "--schema", str(schema),
        ]))
    if args.command == "run":
        script = resolve_catalog_path(catalog["tools"][args.tool]["script"])
        tool_args = args.tool_args[1:] if args.tool_args[:1] == ["--"] else args.tool_args
        raise SystemExit(run_checked([sys.executable, str(script), *tool_args]))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: {exc}") from None

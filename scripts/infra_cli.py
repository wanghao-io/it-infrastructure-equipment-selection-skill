#!/usr/bin/env python3
"""Thin, safe entry point for deterministic Skill tools and contracts."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "assets/tool-catalog.json"
PUBLIC_RUN = "public-run"
EXPOSURES = {PUBLIC_RUN, "public-gated", "lifecycle", "deferred", "internal"}
REQUIRED_TOOL_FIELDS = {
    "script",
    "description",
    "exposure",
    "side_effects",
    "input_contract",
    "applicability",
    "limitations",
    "excluded_reason",
}


def resolve_catalog_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if path == ROOT or ROOT not in path.parents:
        raise ValueError("catalog path escapes the Skill root")
    return path


def load_catalog() -> dict[str, Any]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    tools = catalog.get("tools")
    contracts = catalog.get("contracts")
    if not isinstance(tools, dict) or not isinstance(contracts, dict):
        raise ValueError("tool catalog must contain object-valued 'tools' and 'contracts'")

    catalog_scripts: list[str] = []
    for name, item in tools.items():
        if not isinstance(item, dict):
            raise ValueError(f"catalog tool {name!r} must be an object")
        missing = sorted(REQUIRED_TOOL_FIELDS - set(item))
        if missing:
            raise ValueError(f"catalog tool {name!r} missing fields: {', '.join(missing)}")
        if item["exposure"] not in EXPOSURES:
            raise ValueError(f"catalog tool {name!r} has unsupported exposure {item['exposure']!r}")
        if not isinstance(item["limitations"], list):
            raise ValueError(f"catalog tool {name!r} limitations must be an array")
        if item["exposure"] == PUBLIC_RUN:
            if item["excluded_reason"] is not None:
                raise ValueError(f"public-run tool {name!r} must not have an excluded reason")
            if item["side_effects"] != "stdout-only":
                raise ValueError(f"public-run tool {name!r} must be stdout-only")
            if not isinstance(item.get("example"), list):
                raise ValueError(f"public-run tool {name!r} must provide an example argv array")
        elif not isinstance(item["excluded_reason"], str) or not item["excluded_reason"].strip():
            raise ValueError(f"non-runnable tool {name!r} must explain why it is excluded from run")
        contract = item["input_contract"]
        if contract is not None and contract not in contracts:
            raise ValueError(f"catalog tool {name!r} references unknown contract {contract!r}")
        script = str(item["script"])
        script_path = resolve_catalog_path(script)
        if not script_path.is_file() or script_path.suffix != ".py":
            raise ValueError(f"catalog tool {name!r} does not reference a Python script")
        catalog_scripts.append(script)

    if len(catalog_scripts) != len(set(catalog_scripts)):
        raise ValueError("each script must appear exactly once in the tool catalog")
    actual_scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("*.py")
        if path.is_file()
    }
    catalog_script_set = set(catalog_scripts)
    if catalog_script_set != actual_scripts:
        missing = sorted(actual_scripts - catalog_script_set)
        extra = sorted(catalog_script_set - actual_scripts)
        details = []
        if missing:
            details.append(f"uncatalogued scripts: {', '.join(missing)}")
        if extra:
            details.append(f"unknown scripts: {', '.join(extra)}")
        raise ValueError("; ".join(details))

    for name, value in contracts.items():
        path = resolve_catalog_path(str(value))
        if not path.is_file():
            raise ValueError(f"catalog contract {name!r} does not exist")
    return catalog


def write_child_stderr(stderr: str, *, debug: bool = False) -> None:
    if not stderr:
        return
    if not debug and "Traceback (most recent call last):" in stderr:
        last_line = next((line for line in reversed(stderr.splitlines()) if line.strip()), "tool failed")
        sys.stderr.write(f"error: {last_line}\n")
    else:
        sys.stderr.write(stderr)


def run_checked(command: list[str], *, debug: bool = False, emit_stdout: bool = True) -> int:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if emit_stdout and result.stdout:
        sys.stdout.write(result.stdout)
    elif not emit_stdout and result.returncode and result.stdout:
        write_child_stderr(result.stdout, debug=debug)
    if result.stderr:
        write_child_stderr(result.stderr, debug=debug)
    return result.returncode


def positional_argument_index(arguments: list[str], item: dict[str, Any]) -> int | None:
    """Locate a catalog-declared positional path while skipping known option values."""
    target_position = item.get("input_path_position")
    if target_position is None:
        return None
    value_options = set(item.get("option_value_flags", []))
    positional = 0
    skip_next = False
    for index, value in enumerate(arguments):
        if skip_next:
            skip_next = False
            continue
        if value in value_options:
            skip_next = True
            continue
        if any(value.startswith(f"{option}=") for option in value_options):
            continue
        if value.startswith("-"):
            continue
        if positional == int(target_position):
            return index
        positional += 1
    return None


def prepare_tool_arguments(
    item: dict[str, Any],
    arguments: list[str],
    *,
    relative_to: Path,
) -> tuple[list[str], int | None]:
    prepared = list(arguments)
    input_index = positional_argument_index(prepared, item)
    if input_index is None:
        return prepared, None
    input_path = Path(prepared[input_index]).expanduser()
    if not input_path.is_absolute():
        input_path = (relative_to / input_path).resolve()
    else:
        input_path = input_path.resolve()
    prepared[input_index] = str(input_path)
    return prepared, input_index


def validate_tool_input(
    catalog: dict[str, Any],
    item: dict[str, Any],
    arguments: list[str],
    input_index: int | None,
    *,
    debug: bool,
) -> int:
    contract = item["input_contract"]
    if contract is None or input_index is None:
        return 0
    schema = resolve_catalog_path(catalog["contracts"][contract])
    return run_checked(
        [
            sys.executable,
            str(ROOT / "scripts/validate_json_schemas.py"),
            arguments[input_index],
            "--schema",
            str(schema),
        ],
        debug=debug,
        emit_stdout=False,
    )


def catalog_view(catalog: dict[str, Any], *, include_all: bool) -> dict[str, Any]:
    tools = {
        name: item
        for name, item in catalog["tools"].items()
        if include_all or item["exposure"] == PUBLIC_RUN
    }
    return {
        "catalog_version": catalog["catalog_version"],
        "tools": tools,
        "contracts": catalog["contracts"],
    }


def example_argv(tool: str, item: dict[str, Any]) -> list[str]:
    example, _ = prepare_tool_arguments(item, [str(value) for value in item["example"]], relative_to=ROOT)
    return [sys.executable, str(Path(__file__).resolve()), "run", tool, "--", *example]


def main() -> None:
    caller_cwd = Path.cwd()
    catalog = load_catalog()
    public_tools = sorted(name for name, item in catalog["tools"].items() if item["exposure"] == PUBLIC_RUN)
    parser = argparse.ArgumentParser(
        description="Discover and run deterministic infrastructure calculators; Agent research remains outside this CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List deterministic tools and named contracts")
    list_parser.add_argument("--all", action="store_true", help="Include gated, lifecycle, deferred and internal scripts")
    list_parser.add_argument("--json", action="store_true")
    example_parser = subparsers.add_parser("example", help="Show a cwd-independent example for one public tool")
    example_parser.add_argument("tool", choices=public_tools)
    example_parser.add_argument("--json", action="store_true", help="Print the command as a JSON argv array")
    validate_parser = subparsers.add_parser("validate", help="Validate a JSON file against a named contract")
    validate_parser.add_argument("contract", choices=sorted(catalog["contracts"]))
    validate_parser.add_argument("input", type=Path)
    validate_parser.add_argument("--debug", action="store_true", help="Preserve validator tracebacks for diagnosis")
    run_parser = subparsers.add_parser("run", help="Run a public-run deterministic tool")
    run_parser.add_argument("--debug", action="store_true", help="Preserve child tracebacks for diagnosis")
    run_parser.add_argument("tool", choices=sorted(catalog["tools"]))
    run_parser.add_argument("tool_args", nargs=argparse.REMAINDER, help="arguments passed to the selected tool")
    guide_parser = subparsers.add_parser("guide", help="Run requirement discovery without selecting architecture")
    guide_parser.add_argument("--templates", type=Path)
    guide_parser.add_argument("--list", action="store_true")
    guide_parser.add_argument("--scenario")
    guide_parser.add_argument("--input", type=Path)
    guide_parser.add_argument("--max-questions", type=int, default=7)
    guide_parser.add_argument("--pretty", action="store_true")
    guide_parser.add_argument("--debug", action="store_true")
    server_parser = subparsers.add_parser("server-quotes", help="Validate or compare a versioned server RFQ")
    server_parser.add_argument("action", choices=["validate", "compare"])
    server_parser.add_argument("input", type=Path)
    server_parser.add_argument("--pretty", action="store_true")
    server_parser.add_argument("--debug", action="store_true")
    price_parser = subparsers.add_parser("price-evidence", help="Normalize strict versioned price evidence")
    price_parser.add_argument("input", type=Path)
    price_parser.add_argument("--existing-budget", type=float)
    price_parser.add_argument("--existing-currency")
    price_parser.add_argument("--product-class")
    price_parser.add_argument("--debug", action="store_true")
    migrate_parser = subparsers.add_parser("migrate", help="Dry-run or write a non-destructive v1-to-v2 migration")
    migrate_parser.add_argument("family", choices=["price-evidence", "project-retrospective"])
    migrate_parser.add_argument("input", type=Path)
    migrate_parser.add_argument("--decision-scope-id")
    migrate_parser.add_argument("--output", type=Path)
    migrate_parser.add_argument("--debug", action="store_true")
    project_parser = subparsers.add_parser("project-check", help="Validate explicit evidence/delivery/acceptance records; not real-world truth")
    project_parser.add_argument("family", choices=["project-evidence", "project-delivery", "acceptance-evidence"])
    project_parser.add_argument("input", type=Path)
    project_parser.add_argument("--project-root", type=Path)
    project_parser.add_argument("--check-files", action="store_true")
    project_parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.command == "list":
        view = catalog_view(catalog, include_all=args.all)
        if args.json:
            print(json.dumps(view, ensure_ascii=False, indent=2))
        else:
            for name, item in view["tools"].items():
                print(f"{name:24} [{item['exposure']}] {item['description']}")
                if item["excluded_reason"]:
                    print(f"  excluded from run: {item['excluded_reason']}")
            print("\nContracts:")
            for name in view["contracts"]:
                print(f"  {name}")
        return
    if args.command == "example":
        argv = example_argv(args.tool, catalog["tools"][args.tool])
        command_text = subprocess.list2cmdline(argv) if sys.platform == "win32" else shlex.join(argv)
        print(json.dumps(argv, ensure_ascii=False, indent=2) if args.json else command_text)
        return
    if args.command == "validate":
        schema = resolve_catalog_path(catalog["contracts"][args.contract])
        raise SystemExit(run_checked([
            sys.executable,
            str(ROOT / "scripts/validate_json_schemas.py"),
            str((caller_cwd / args.input).resolve() if not args.input.is_absolute() else args.input.resolve()),
            "--schema",
            str(schema),
        ], debug=args.debug))
    if args.command == "guide":
        command = [sys.executable, str(ROOT / "scripts/guide_requirements.py")]
        if args.templates:
            template_path = (caller_cwd / args.templates).resolve() if not args.templates.is_absolute() else args.templates.resolve()
            schema = resolve_catalog_path(catalog["contracts"]["scenario-template-v1"])
            status = run_checked(
                [sys.executable, str(ROOT / "scripts/validate_json_schemas.py"), str(template_path), "--schema", str(schema)],
                debug=args.debug,
                emit_stdout=False,
            )
            if status:
                raise SystemExit(status)
            command.extend(["--templates", str(template_path)])
        if args.list:
            command.append("--list")
        if args.scenario:
            command.extend(["--scenario", args.scenario])
        if args.input:
            input_path = (caller_cwd / args.input).resolve() if not args.input.is_absolute() else args.input.resolve()
            command.extend(["--input", str(input_path)])
        command.extend(["--max-questions", str(args.max_questions)])
        if args.pretty:
            command.append("--pretty")
        raise SystemExit(run_checked(command, debug=args.debug))
    if args.command == "project-check":
        command = [sys.executable, str(ROOT / "scripts/validate_project_delivery.py"),
                   args.family, str((caller_cwd / args.input).resolve())]
        if args.project_root:
            command.extend(["--project-root", str((caller_cwd / args.project_root).resolve())])
        if args.check_files:
            command.append("--check-files")
        raise SystemExit(run_checked(command, debug=args.debug))
    if args.command == "server-quotes":
        input_path = (caller_cwd / args.input).resolve() if not args.input.is_absolute() else args.input.resolve()
        data = json.loads(
            input_path.read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-standard JSON numeric constant is not allowed: {value}")),
        )
        version = data.get("schema_version") if isinstance(data, dict) else None
        contract = f"server-rfq-v{version}"
        if contract not in catalog["contracts"]:
            raise SystemExit(f"error: unsupported server-rfq version {version!r}")
        if args.action == "compare" and version != 2:
            raise SystemExit("error: exact server comparison requires server-rfq-v2; v1 is a coarse minimum gate only")
        schema = resolve_catalog_path(catalog["contracts"][contract])
        status = run_checked(
            [sys.executable, str(ROOT / "scripts/validate_json_schemas.py"), str(input_path), "--schema", str(schema)],
            debug=args.debug,
            emit_stdout=False,
        )
        if status:
            raise SystemExit(status)
        script = "validate_server_quote.py" if args.action == "validate" else "compare_server_quotes.py"
        command = [sys.executable, str(ROOT / "scripts" / script), str(input_path)]
        if args.pretty:
            command.append("--pretty")
        raise SystemExit(run_checked(command, debug=args.debug))
    if args.command == "price-evidence":
        input_path = (caller_cwd / args.input).resolve() if not args.input.is_absolute() else args.input.resolve()
        command = [
            sys.executable,
            str(ROOT / "scripts/normalize_price_evidence.py"),
            str(input_path),
            "--summary",
            "--strict-contract",
        ]
        if args.existing_budget is not None:
            if not args.existing_currency:
                raise SystemExit("error: --existing-currency is required with --existing-budget")
            command.extend(["--existing-budget", str(args.existing_budget), "--existing-currency", args.existing_currency])
        if args.product_class:
            command.extend(["--product-class", args.product_class])
        raise SystemExit(run_checked(command, debug=args.debug))
    if args.command == "migrate":
        input_path = (caller_cwd / args.input).resolve() if not args.input.is_absolute() else args.input.resolve()
        command = [sys.executable, str(ROOT / "scripts/migrate_schema.py"), args.family, str(input_path)]
        if args.decision_scope_id:
            command.extend(["--decision-scope-id", args.decision_scope_id])
        if args.output:
            output_path = (caller_cwd / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
            command.extend(["--output", str(output_path)])
        raise SystemExit(run_checked(command, debug=args.debug))
    if args.command == "run":
        item = catalog["tools"][args.tool]
        if item["exposure"] != PUBLIC_RUN:
            raise SystemExit(
                f"error: {args.tool!r} is not available through run: {item['excluded_reason']}"
            )
        script = resolve_catalog_path(item["script"])
        tool_args = args.tool_args[1:] if args.tool_args[:1] == ["--"] else args.tool_args
        tool_args, input_index = prepare_tool_arguments(item, tool_args, relative_to=caller_cwd)
        validation_status = validate_tool_input(
            catalog,
            item,
            tool_args,
            input_index,
            debug=args.debug,
        )
        if validation_status:
            raise SystemExit(validation_status)
        raise SystemExit(run_checked([sys.executable, str(script), *tool_args], debug=args.debug))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: {exc}") from None

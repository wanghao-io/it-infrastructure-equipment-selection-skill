#!/usr/bin/env python3
"""Auditable, non-destructive v1-to-v2 contract migration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_json_schemas import validate, validate_retrospective_semantics

ROOT = Path(__file__).resolve().parents[1]


def migrate_price(instance: dict[str, Any], scope: str | None) -> tuple[dict[str, Any], list[str]]:
    if instance.get("schema_version") != 1:
        raise ValueError("price-evidence migration requires schema_version 1")
    if not scope:
        raise ValueError("--decision-scope-id is required; migration will not invent decision scope")
    migrated = {"schema_version": 2, "decision_scope_id": scope, "items": []}
    changes = ["schema_version: 1 -> 2", f"decision_scope_id: {scope}"]
    for index, source in enumerate(instance.get("items", [])):
        if source.get("technical_fit_status") not in {"PASS", "CONDITIONAL", "FAIL"}:
            raise ValueError(f"$.items[{index}].technical_fit_status: explicit value required")
        if type(source.get("eligible_for_pricing")) is not bool:
            raise ValueError(f"$.items[{index}].eligible_for_pricing: explicit boolean required")
        item = dict(source)
        if "evidence_level" in item:
            item["declared_evidence_level"] = item.pop("evidence_level")
            changes.append(f"$.items[{index}].evidence_level -> declared_evidence_level")
        migrated["items"].append(item)
    return migrated, changes


def migrate_retrospective(instance: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    if instance.get("schema_version") != 1:
        raise ValueError("project-retrospective migration requires schema_version 1")
    migrated = dict(instance)
    migrated["schema_version"] = 2
    return migrated, ["schema_version: 1 -> 2"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run a conservative v1-to-v2 schema migration")
    parser.add_argument("contract", choices=["price-evidence", "project-retrospective"])
    parser.add_argument("input", type=Path)
    parser.add_argument("--decision-scope-id")
    parser.add_argument("--output", type=Path, help="Write only to a new path; existing files are never overwritten")
    args = parser.parse_args()
    instance = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(instance, dict):
        raise SystemExit("$: expected object envelope")
    try:
        if args.contract == "price-evidence":
            migrated, changes = migrate_price(instance, args.decision_scope_id)
            schema_path = ROOT / "schemas/v2/price-evidence.schema.json"
        else:
            migrated, changes = migrate_retrospective(instance)
            schema_path = ROOT / "schemas/v2/project-retrospective.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = validate(migrated, schema)
        if args.contract == "project-retrospective":
            errors.extend(validate_retrospective_semantics(migrated))
        if errors:
            raise ValueError("target validation failed:\n" + "\n".join(errors))
    except ValueError as exc:
        raise SystemExit(str(exc)) from None

    report = {"status": "ready", "source_unchanged": True, "changes": changes, "result": migrated}
    if args.output:
        if args.output.exists():
            raise SystemExit(f"refusing to overwrite existing output: {args.output}")
        args.output.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["written_to"] = str(args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

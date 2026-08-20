#!/usr/bin/env python3
"""Validate bundled examples against the Skill's JSON Schema contracts.

This intentionally implements the conservative subset used by bundled schemas so
CI and installed Skills do not need a third-party Python package. The schemas are
Draft 2020-12 documents and remain usable by standard JSON Schema validators.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class SchemaError(ValueError):
    pass


def resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise SchemaError(f"only local JSON Pointer refs are supported: {ref}")
    value: Any = root
    for part in ref[2:].split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    if not isinstance(value, dict):
        raise SchemaError(f"reference does not resolve to a schema object: {ref}")
    return value


def type_matches(value: Any, expected: str) -> bool:
    finite_number = (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and (not isinstance(value, float) or math.isfinite(value))
    )
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": finite_number,
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": type(value) is bool,
        "null": value is None,
    }.get(expected, False)


def validate(instance: Any, schema: dict[str, Any], *, root: dict[str, Any] | None = None, path: str = "$") -> list[str]:
    root = schema if root is None else root
    if "$ref" in schema:
        return validate(instance, resolve_ref(root, schema["$ref"]), root=root, path=path)

    for keyword in ("allOf", "anyOf", "oneOf"):
        if keyword not in schema:
            continue
        results = [validate(instance, child, root=root, path=path) for child in schema[keyword]]
        passed = sum(not errors for errors in results)
        if keyword == "allOf" and passed != len(results):
            return [f"{path}: does not satisfy allOf"]
        if keyword == "anyOf" and passed == 0:
            return [f"{path}: does not satisfy anyOf"]
        if keyword == "oneOf" and passed != 1:
            return [f"{path}: does not satisfy exactly one oneOf branch"]

    errors: list[str] = []
    expected = schema.get("type")
    if expected is not None:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(type_matches(instance, item) for item in choices):
            return [f"{path}: expected type {'/'.join(choices)}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value is outside enum")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        errors.extend(f"{path}.{key}: required property missing" for key in required if key not in instance)
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(validate(value, properties[key], root=root, path=child_path))
            elif isinstance(additional, dict):
                errors.extend(validate(value, additional, root=root, path=child_path))
            elif additional is False:
                errors.append(f"{child_path}: additional property not allowed")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than minItems")
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in instance}) != len(instance):
            errors.append(f"{path}: items are not unique")
        if isinstance(schema.get("items"), dict):
            for index, value in enumerate(instance):
                errors.extend(validate(value, schema["items"], root=root, path=f"{path}[{index}]"))

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{path}: does not match pattern")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(instance)
            except ValueError:
                errors.append(f"{path}: invalid ISO date")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: not above exclusiveMinimum")
    return errors


def validate_file(schema_path: Path, instance_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        return [f"{schema_path}: must declare Draft 2020-12"]
    try:
        instance = json.loads(
            instance_path.read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-standard JSON numeric constant is not allowed: {value}")
            ),
        )
    except ValueError as exc:
        return [f"$: invalid strict JSON: {exc}"]
    errors = validate(instance, schema)
    if schema_path.name == "project-retrospective.schema.json":
        errors.extend(validate_retrospective_semantics(instance))
    return errors


def validate_retrospective_semantics(instance: Any) -> list[str]:
    """Reject evidence claims that exceed the documented project stage."""
    if not isinstance(instance, dict):
        return []
    stage_order = {
        "requirements": 0, "design": 1, "rfq": 2,
        "awarded": 3, "implemented": 4, "operational": 5,
    }
    evidence_minimum = {
        "design-baseline-only": "requirements",
        "current-quotes": "rfq",
        "award-record": "awarded",
        "settlement-record": "implemented",
        "operational-measurement": "operational",
    }
    errors: list[str] = []
    stage = instance.get("project_stage")
    evidence = instance.get("evidence_status")
    minimum = evidence_minimum.get(evidence)
    if stage in stage_order and minimum and stage_order[stage] < stage_order[minimum]:
        errors.append(f"$.evidence_status: {evidence} exceeds project_stage {stage}")

    budget = instance.get("budget")
    if evidence == "award-record":
        if not isinstance(budget, dict) or "awarded" not in budget:
            errors.append("$.budget.awarded: required for award-record")
        if not isinstance(budget, dict) or "currency" not in budget:
            errors.append("$.budget.currency: required for award-record")
    if evidence == "settlement-record":
        if not isinstance(budget, dict) or "settled" not in budget:
            errors.append("$.budget.settled: required for settlement-record")
        if not isinstance(budget, dict) or "currency" not in budget:
            errors.append("$.budget.currency: required for settlement-record")
    if instance.get("schema_version") == 2 and evidence in {"award-record", "settlement-record"}:
        final_key = "awarded" if evidence == "award-record" else "settled"
        if isinstance(budget, dict) and final_key in budget and any(key in budget for key in ("initial", "revised")):
            if budget.get("technical_scope_normalized") is not True:
                errors.append("$.budget.technical_scope_normalized: true required for forecast comparison")
            if budget.get("commercial_scope_normalized") is not True:
                errors.append("$.budget.commercial_scope_normalized: true required for forecast comparison")
    if evidence == "operational-measurement":
        measurements = instance.get("operational_measurements")
        if not isinstance(measurements, list) or not measurements:
            errors.append("$.operational_measurements: structured records required for operational-measurement")
    return errors


def validate_catalog(root: Path = ROOT) -> list[str]:
    catalog = json.loads((root / "schemas/catalog.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    for name, current in catalog.get("current_contracts", {}).items():
        supported = catalog.get("supported_contracts", {}).get(name, [])
        if current not in supported:
            errors.append(f"schemas/catalog.json: current {name} v{current} is not supported")
    seen_ids: set[str] = set()
    for mapping in catalog["mappings"]:
        schema_path = root / mapping["schema"]
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_id = schema.get("$id", "")
        if not schema_id:
            errors.append(f"{mapping['schema']}: missing $id")
        elif schema_id in seen_ids:
            errors.append(f"{mapping['schema']}: duplicate $id {schema_id}")
        seen_ids.add(schema_id)
        if "/v2/" in mapping["schema"] and "/v2/" not in schema_id:
            errors.append(f"{mapping['schema']}: v2 schema must have a versioned $id")
        for example in mapping["examples"]:
            instance_path = root / example
            errors.extend(f"{example}: {error}" for error in validate_file(schema_path, instance_path))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate JSON inputs against bundled Skill schemas")
    parser.add_argument("instance", nargs="?", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--catalog", action="store_true")
    args = parser.parse_args()
    if args.catalog or args.instance is None:
        errors = validate_catalog()
    else:
        if args.schema is None:
            parser.error("--schema is required with an instance")
        errors = validate_file(args.schema, args.instance)
    if errors:
        raise SystemExit("\n".join(errors))
    print("JSON Schema validation passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Guided requirement discovery using non-prescriptive scenario templates.

Templates suggest assumptions and high-value questions. They never choose an
architecture or silently convert defaults into mandatory project facts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets" / "scenario-templates.json"

UNRESOLVED_MARKERS = (
    "tbd",
    "unknown",
    "needs confirmation",
    "to be confirmed",
    "待确认",
    "未确认",
    "待定",
    "未知",
)


def load_templates(path: Path = DEFAULT_TEMPLATE_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    templates = data.get("templates", [])
    if not isinstance(templates, list) or not templates:
        raise ValueError("Scenario template file must contain a non-empty 'templates' list.")
    return data


def template_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["id"]): item for item in data["templates"]}


def is_unresolved(value: Any) -> bool:
    """Return True when a supplied requirement value is absent or explicitly unresolved."""
    if value is None:
        return True
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return True
        lowered = text.lower()
        return any(marker in lowered for marker in UNRESOLVED_MARKERS)
    if isinstance(value, dict):
        if not value:
            return True
        return any(is_unresolved(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        if not value:
            return True
        return any(is_unresolved(v) for v in value)
    return False


def item_is_unresolved(item: dict[str, Any], value: Any) -> bool:
    """Evaluate a field, including optional required_parts for composite requirements."""
    if is_unresolved(value):
        return True

    required_parts = [str(x) for x in item.get("required_parts", [])]
    if not required_parts:
        return False

    # Composite requirements must be supplied structurally so partial answers
    # such as only RTO (without RPO) cannot accidentally look complete.
    if not isinstance(value, dict):
        return True

    for part in required_parts:
        if part not in value or is_unresolved(value.get(part)):
            return True
    return False


def analyze_requirements(
    scenario_id: str,
    supplied: dict[str, Any] | None = None,
    *,
    max_questions: int = 7,
    template_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    supplied = supplied or {}
    data = template_data or load_templates()
    index = template_index(data)
    if scenario_id not in index:
        raise ValueError(f"Unknown scenario '{scenario_id}'. Available: {', '.join(sorted(index))}")

    template = index[scenario_id]
    required = sorted(
        template.get("required_fields", []),
        key=lambda item: (int(item.get("priority", 99)), str(item.get("key", ""))),
    )

    missing = []
    missing_parts: dict[str, list[str]] = {}
    questions = []
    for item in required:
        key = str(item["key"])
        value = supplied.get(key)
        unresolved = item_is_unresolved(item, value)
        if unresolved:
            missing.append(key)
            parts = [str(x) for x in item.get("required_parts", [])]
            if parts:
                if isinstance(value, dict):
                    missing_parts[key] = [part for part in parts if part not in value or is_unresolved(value.get(part))]
                else:
                    missing_parts[key] = parts
            if len(questions) < max_questions:
                questions.append(
                    {
                        "key": key,
                        "question": item.get("question", key),
                        "priority": int(item.get("priority", 99)),
                        "required_parts": item.get("required_parts", []),
                    }
                )

    suggested = {
        key: value
        for key, value in template.get("suggested_assumptions", {}).items()
        if key not in supplied or is_unresolved(supplied.get(key))
    }

    return {
        "scenario": scenario_id,
        "scenario_name": template.get("name", scenario_id),
        "known_fields": supplied,
        "missing_required_fields": missing,
        "missing_required_parts": missing_parts,
        "questions": questions,
        "suggested_assumptions": suggested,
        "guardrails": template.get("guardrails", []),
        "ready_for_architecture": len(missing) == 0,
        "note": (
            "Suggested assumptions are not project facts. Confirm or explicitly carry them as assumptions; "
            "they must not force HCI, HA, core switching, firewall, Xinchuang or other architecture choices. "
            "Composite requirements are resolved only when every required part is supplied; partial answers remain TBD."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a concise guided requirement-discovery checklist.")
    parser.add_argument("--templates", type=Path, default=DEFAULT_TEMPLATE_PATH)
    parser.add_argument("--list", action="store_true", help="List available scenario IDs")
    parser.add_argument("--scenario", help="Scenario template ID")
    parser.add_argument("--input", type=Path, help="Optional JSON file containing already-known project fields")
    parser.add_argument("--max-questions", type=int, default=7)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    data = load_templates(args.templates)
    if args.list:
        for item in data["templates"]:
            print(f"{item['id']}\t{item.get('name', '')}")
        return

    if not args.scenario:
        parser.error("--scenario is required unless --list is used")

    supplied: dict[str, Any] = {}
    if args.input:
        supplied = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(supplied, dict):
            raise ValueError("Requirement input must be a JSON object.")

    result = analyze_requirements(
        args.scenario,
        supplied,
        max_questions=max(1, args.max_questions),
        template_data=data,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

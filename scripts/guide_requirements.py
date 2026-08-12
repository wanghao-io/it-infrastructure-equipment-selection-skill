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


def load_templates(path: Path = DEFAULT_TEMPLATE_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    templates = data.get("templates", [])
    if not isinstance(templates, list) or not templates:
        raise ValueError("Scenario template file must contain a non-empty 'templates' list.")
    return data


def template_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["id"]): item for item in data["templates"]}


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
    questions = []
    for item in required:
        key = str(item["key"])
        value = supplied.get(key)
        unresolved = value is None or value == "" or value == "TBD"
        if unresolved:
            missing.append(key)
            if len(questions) < max_questions:
                questions.append(
                    {
                        "key": key,
                        "question": item.get("question", key),
                        "priority": int(item.get("priority", 99)),
                    }
                )

    suggested = {
        key: value
        for key, value in template.get("suggested_assumptions", {}).items()
        if key not in supplied or supplied.get(key) in (None, "", "TBD")
    }

    return {
        "scenario": scenario_id,
        "scenario_name": template.get("name", scenario_id),
        "known_fields": supplied,
        "missing_required_fields": missing,
        "questions": questions,
        "suggested_assumptions": suggested,
        "guardrails": template.get("guardrails", []),
        "ready_for_architecture": len(missing) == 0,
        "note": (
            "Suggested assumptions are not project facts. Confirm or explicitly carry them as assumptions; "
            "they must not force HCI, HA, core switching, firewall, Xinchuang or other architecture choices."
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

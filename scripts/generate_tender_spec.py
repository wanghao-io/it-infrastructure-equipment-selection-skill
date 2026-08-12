#!/usr/bin/env python3
"""Generate a neutral tender/RFQ specification from structured JSON requirements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_LEVELS = {"Mandatory", "Recommended", "Optional"}


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate(data: dict[str, Any]) -> str:
    title = data.get("title", "Technical Tender / RFQ Specification")
    scope = data.get("scope", "")
    assumptions = data.get("assumptions", [])
    requirements = data.get("requirements", [])
    if not requirements:
        raise ValueError("Input must contain a non-empty 'requirements' list.")

    lines = [f"# {title}", ""]
    if scope:
        lines.extend(["## Scope", "", str(scope), ""])

    if assumptions:
        lines.extend(["## Assumptions / TBD", ""])
        for item in assumptions:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["## Technical Requirements", ""])
    lines.append("| ID | Category | Requirement | Level | Acceptance / Evidence |")
    lines.append("|---|---|---|---|---|")

    seen_ids: set[str] = set()
    for idx, req in enumerate(requirements, start=1):
        rid = str(req.get("id") or f"R{idx:03d}")
        if rid in seen_ids:
            raise ValueError(f"Duplicate requirement id: {rid}")
        seen_ids.add(rid)
        level = str(req.get("level", "Mandatory"))
        if level not in VALID_LEVELS:
            level = "Mandatory"
        category = str(req.get("category", "General"))
        text = str(req.get("requirement", "TBD")).replace("|", "\\|")
        evidence = str(req.get("evidence", "Supplier response + official technical evidence where applicable")).replace("|", "\\|")
        lines.append(f"| {rid} | {category} | {text} | {level} | {evidence} |")

    lines.extend([
        "",
        "## Supplier Compliance Response",
        "",
        "| ID | Supplier response | Evidence reference | Result | Notes |",
        "|---|---|---|---|---|",
    ])
    for rid in seen_ids:
        lines.append(f"| {rid} |  |  | Needs confirmation |  |")

    lines.extend([
        "",
        "## Procurement Notes",
        "",
        "- Requirements should remain vendor-neutral unless a compatibility or policy constraint is explicitly justified.",
        "- Exact configured BOM, licenses, accessories, tax, support and implementation scope must be confirmed before commercial comparison.",
        "- Values marked TBD or based on assumptions require project confirmation before tender release.",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a vendor-neutral tender/RFQ specification from JSON.")
    parser.add_argument("input", help="JSON requirements file")
    parser.add_argument("-o", "--output", help="Markdown output path; stdout if omitted")
    args = parser.parse_args()

    text = generate(load_json(args.input))
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()

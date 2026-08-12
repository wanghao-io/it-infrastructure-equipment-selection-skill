#!/usr/bin/env python3
"""Generate a weighted vendor/model comparison matrix from JSON input.

This tool does not contain vendor rankings. It scores project-specific candidates
using caller-supplied criteria, evidence and hard-gate results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_GATE = {"PASS", "CONDITIONAL", "FAIL"}


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def overall_gate(gates: list[dict[str, Any]]) -> str:
    statuses = {str(g.get("status", "CONDITIONAL")).upper() for g in gates}
    if "FAIL" in statuses:
        return "FAIL"
    if "CONDITIONAL" in statuses:
        return "CONDITIONAL"
    return "PASS"


def build_report(data: dict[str, Any]) -> str:
    criteria = data.get("criteria", [])
    candidates = data.get("candidates", [])
    if not criteria or not candidates:
        raise ValueError("Input must contain non-empty 'criteria' and 'candidates'.")

    total_weight = sum(float(c.get("weight", 0)) for c in criteria)
    if total_weight <= 0:
        raise ValueError("Total criterion weight must be greater than zero.")

    lines: list[str] = ["# Vendor / Model Comparison", ""]
    lines.append("Weighted scores are project-specific and do not represent permanent vendor rankings.")
    lines.append("")

    headers = ["Criterion", "Weight"] + [c.get("name", "Unnamed") for c in candidates]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")

    weighted_totals: dict[str, float] = {c.get("name", "Unnamed"): 0.0 for c in candidates}

    for criterion in criteria:
        key = criterion.get("key")
        label = criterion.get("name", key or "Unnamed")
        weight = float(criterion.get("weight", 0))
        norm_weight = weight / total_weight
        row = [label, f"{norm_weight * 100:.1f}%"]
        for candidate in candidates:
            name = candidate.get("name", "Unnamed")
            score_obj = candidate.get("scores", {}).get(key, {})
            score = float(score_obj.get("score", 0))
            evidence = score_obj.get("evidence", "Needs confirmation")
            weighted_totals[name] += score * norm_weight
            row.append(f"{score:.1f}/10 ({evidence})")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Gate Results", ""])
    for candidate in candidates:
        name = candidate.get("name", "Unnamed")
        gates = candidate.get("gates", [])
        gate = overall_gate(gates)
        lines.append(f"### {name} — {gate}")
        if not gates:
            lines.append("- No hard gates supplied; treat result as CONDITIONAL until mandatory requirements are checked.")
        for item in gates:
            status = str(item.get("status", "CONDITIONAL")).upper()
            if status not in VALID_GATE:
                status = "CONDITIONAL"
            lines.append(f"- {status}: {item.get('requirement', 'Unnamed requirement')} — {item.get('note', '')}".rstrip())
        lines.append("")

    lines.extend(["## Weighted Score", ""])
    lines.append("| Candidate | Gate | Score / 10 |")
    lines.append("|---|---|---:|")
    ranked: list[tuple[str, str, float]] = []
    for candidate in candidates:
        name = candidate.get("name", "Unnamed")
        gate = overall_gate(candidate.get("gates", [])) if candidate.get("gates") else "CONDITIONAL"
        ranked.append((name, gate, weighted_totals[name]))
    ranked.sort(key=lambda x: (x[1] == "FAIL", -x[2]))
    for name, gate, score in ranked:
        lines.append(f"| {name} | {gate} | {score:.2f} |")

    lines.extend([
        "",
        "> A weighted score never overrides a failed mandatory requirement. Verify exact configuration, lifecycle, licensing, support and price evidence before procurement.",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a project-specific vendor/model comparison matrix.")
    parser.add_argument("input", help="JSON input file")
    parser.add_argument("-o", "--output", help="Markdown output file; stdout if omitted")
    args = parser.parse_args()

    report = build_report(load_json(args.input))
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()

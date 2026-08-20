#!/usr/bin/env python3
"""Generate a requirement-gated vendor/model comparison matrix from JSON input.

The tool has no permanent vendor rankings. Mandatory constraints are evaluated
first; only then are preference criteria scored. A failed mandatory requirement
can never be rescued by a weighted score.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from contracts import is_unresolved

VALID_GATE = {"PASS", "CONDITIONAL", "FAIL"}
GATE_ORDER = {"PASS": 0, "CONDITIONAL": 1, "FAIL": 2}


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def overall_gate(gates: list[dict[str, Any]]) -> str:
    if not gates:
        return "CONDITIONAL"
    statuses = {str(g.get("status", "CONDITIONAL")).upper() for g in gates}
    if not statuses.issubset(VALID_GATE):
        return "CONDITIONAL"
    if "FAIL" in statuses:
        return "FAIL"
    if "CONDITIONAL" in statuses:
        return "CONDITIONAL"
    return "PASS"


def compare_value(actual: Any, operator: str, expected: Any) -> bool:
    op = operator.lower()
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "min":
        return float(actual) >= float(expected)
    if op == "max":
        return float(actual) <= float(expected)
    if op == "in":
        return actual in expected
    if op == "contains":
        return expected in actual
    if op == "truthy":
        if type(actual) is not bool:
            raise ValueError("truthy requires a JSON boolean")
        return actual
    if op == "falsy":
        if type(actual) is not bool:
            raise ValueError("falsy requires a JSON boolean")
        return not actual
    raise ValueError(f"Unsupported constraint operator: {operator}")


def constraint_gates(
    constraints: list[dict[str, Any]],
    attributes: dict[str, Any],
) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    for rule in constraints:
        if str(rule.get("severity", "mandatory")).lower() != "mandatory":
            continue
        key = str(rule.get("key", ""))
        label = rule.get("name") or rule.get("requirement") or key or "Unnamed requirement"
        operator = str(rule.get("operator", "eq"))
        expected = rule.get("value")
        if key not in attributes or is_unresolved(attributes.get(key)):
            gates.append(
                {
                    "status": "CONDITIONAL",
                    "requirement": label,
                    "note": f"Missing candidate attribute '{key}'; confirmation required.",
                    "source": "constraint-engine",
                }
            )
            continue
        actual = attributes[key]
        try:
            passed = compare_value(actual, operator, expected)
        except (TypeError, ValueError) as exc:
            gates.append(
                {
                    "status": "CONDITIONAL",
                    "requirement": label,
                    "note": f"Could not evaluate {key}: {exc}",
                    "source": "constraint-engine",
                }
            )
            continue
        gates.append(
            {
                "status": "PASS" if passed else "FAIL",
                "requirement": label,
                "note": f"{key}={actual!r}; rule {operator} {expected!r}",
                "source": "constraint-engine",
            }
        )
    return gates


def score_candidates(data: dict[str, Any]) -> list[dict[str, Any]]:
    criteria = data.get("criteria", [])
    candidates = data.get("candidates", [])
    constraints = data.get("constraints", [])
    if not criteria or not candidates:
        raise ValueError("Input must contain non-empty 'criteria' and 'candidates'.")

    weights = [float(c.get("weight", 0)) for c in criteria]
    if any(not math.isfinite(weight) or weight < 0 for weight in weights):
        raise ValueError("Criterion weights must be finite and non-negative.")
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("Total criterion weight must be greater than zero.")

    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        name = candidate.get("name", "Unnamed")
        candidate_id = str(candidate.get("candidate_id", f"candidate-{index + 1}")).strip()
        if not candidate_id or candidate_id in seen_ids:
            raise ValueError("Each candidate must have a unique non-empty candidate_id.")
        seen_ids.add(candidate_id)
        weighted_total = 0.0
        for criterion in criteria:
            key = criterion.get("key")
            weight = float(criterion.get("weight", 0)) / total_weight
            score_obj = candidate.get("scores", {}).get(key, {})
            score = float(score_obj.get("score", 0))
            if not math.isfinite(score):
                raise ValueError(f"{name}: score for '{key}' must be finite")
            if not 0 <= score <= 10:
                raise ValueError(f"{name}: score for '{key}' must be between 0 and 10")
            weighted_total += score * weight

        gates = list(candidate.get("gates", []))
        if constraints:
            gates.extend(constraint_gates(constraints, candidate.get("attributes", {})))
        gate = overall_gate(gates)

        rows.append(
            {
                "name": name,
                "candidate_id": candidate_id,
                "input_index": index,
                "gate": gate,
                "score": weighted_total,
                "gates": gates,
                "candidate": candidate,
            }
        )

    rows.sort(key=lambda item: (GATE_ORDER[item["gate"]], -item["score"], item["name"]))
    return rows


def build_report(data: dict[str, Any]) -> str:
    criteria = data.get("criteria", [])
    candidates = data.get("candidates", [])
    if not criteria or not candidates:
        raise ValueError("Input must contain non-empty 'criteria' and 'candidates'.")

    total_weight = sum(float(c.get("weight", 0)) for c in criteria)
    if total_weight <= 0:
        raise ValueError("Total criterion weight must be greater than zero.")

    ranked = score_candidates(data)
    row_by_index = {item["input_index"]: item for item in ranked}

    lines: list[str] = ["# Vendor / Model Comparison", ""]
    lines.append(
        "Mandatory constraints are evaluated before preference scoring. Scores are project-specific, not permanent vendor rankings."
    )
    lines.append("")

    headers = ["Criterion", "Weight"] + [c.get("name", "Unnamed") for c in candidates]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")

    for criterion in criteria:
        key = criterion.get("key")
        label = criterion.get("name", key or "Unnamed")
        weight = float(criterion.get("weight", 0))
        norm_weight = weight / total_weight
        row = [label, f"{norm_weight * 100:.1f}%"]
        for candidate in candidates:
            score_obj = candidate.get("scores", {}).get(key, {})
            score = float(score_obj.get("score", 0))
            evidence = score_obj.get("evidence", "Needs confirmation")
            row.append(f"{score:.1f}/10 ({evidence})")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Mandatory Gate Results", ""])
    for index, candidate in enumerate(candidates):
        name = candidate.get("name", "Unnamed")
        info = row_by_index[index]
        lines.append(f"### {name} — {info['gate']}")
        if not info["gates"]:
            lines.append("- CONDITIONAL: No mandatory gates supplied; mandatory requirements still need confirmation.")
        for item in info["gates"]:
            status = str(item.get("status", "CONDITIONAL")).upper()
            if status not in VALID_GATE:
                status = "CONDITIONAL"
            lines.append(
                f"- {status}: {item.get('requirement', 'Unnamed requirement')} — {item.get('note', '')}".rstrip()
            )
        lines.append("")

    lines.extend(["## Recommendation Order", ""])
    lines.append("| Rank | Candidate | Gate | Preference score / 10 | Decision |")
    lines.append("|---:|---|---|---:|---|")
    rank = 0
    for item in ranked:
        if item["gate"] == "PASS":
            rank += 1
            decision = "Eligible; rank by preference score after mandatory fit."
            rank_text = str(rank)
        elif item["gate"] == "CONDITIONAL":
            decision = "Not yet eligible for final recommendation; resolve missing mandatory evidence."
            rank_text = "—"
        else:
            decision = "Excluded by mandatory requirement."
            rank_text = "—"
        score_text = f"{item['score']:.2f}" if item["gate"] == "PASS" else "N/A"
        lines.append(f"| {rank_text} | {item['name']} | {item['gate']} | {score_text} | {decision} |")

    lines.extend(
        [
            "",
            "> PASS candidates outrank CONDITIONAL candidates regardless of preference score. "
            "FAIL candidates are excluded. Weighted scoring never overrides a failed or unresolved mandatory requirement.",
        ]
    )
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

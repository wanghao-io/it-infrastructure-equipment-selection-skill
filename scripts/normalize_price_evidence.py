#!/usr/bin/env python3
"""Normalize and rank procurement price evidence.

The key pricing rule is that a current exact-configuration quotation should
outweigh lower-match historical or generic model-family prices when deriving
an enterprise equipment budget anchor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


DEFAULT_MATCH_WEIGHTS: Dict[str, float] = {
    "cpu": 0.15,
    "memory": 0.10,
    "ssd": 0.15,
    "hdd": 0.15,
    "raid": 0.15,
    "network": 0.05,
    "power": 0.05,
    "warranty": 0.10,
    "tax": 0.05,
    "accessories": 0.05,
}

FORMAL_CURRENT_SOURCES = {
    "manufacturer-direct-quote",
    "official-store-quote",
    "authorized-channel-quote",
    # legacy names kept for compatibility
    "official-quote",
    "authorized-channel",
}

CURRENT_MARKET_SOURCES = {
    "enterprise-marketplace-quote",
    "enterprise-marketplace",
    "retail-exact-quote",
}

HISTORICAL_SOURCES = {"government-award", "public-procurement-award"}
COMPONENT_SOURCES = {"component-estimate", "component-cost-model"}
GENERIC_SOURCES = {"generic-listing", "retail", "model-family-listing"}
ESTIMATE_SOURCES = {"engineering-estimate", "estimate"}


def _number(value: Any) -> float:
    if value is True:
        return 1.0
    if value is False or value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp01(value: Any) -> float:
    return max(0.0, min(1.0, _number(value)))


def normalized_cost(item: Mapping[str, Any]) -> float:
    """Return project-comparable cost using all disclosed commercial scope."""
    base = _number(item.get("hardware_price", item.get("price", 0)))
    accessories = _number(item.get("mandatory_accessories", 0))
    licenses = _number(item.get("required_licenses", 0))
    support = _number(item.get("warranty_support", 0))
    implementation = _number(item.get("required_implementation", 0))
    tax = _number(item.get("tax_amount", 0))
    shipping = _number(item.get("shipping", 0))
    return base + accessories + licenses + support + implementation + tax + shipping


def configuration_match_score(
    item: Mapping[str, Any],
    weights: Optional[Mapping[str, float]] = None,
) -> Optional[float]:
    """Calculate a 0..1 configuration match score.

    Explicit ``configuration_match_score`` or ``exact_configuration_match``
    may be used when the caller already performed a device-specific match.
    Otherwise the default server-oriented weighted field model is used.
    Missing fields are treated as unknown/non-matching, not silently as 1.0.
    """
    if item.get("exact_configuration_match") is True:
        return 1.0

    if item.get("configuration_match_score") is not None:
        return round(_clamp01(item["configuration_match_score"]), 4)

    match = item.get("configuration_match")
    if not isinstance(match, Mapping):
        return None

    selected_weights = dict(weights or item.get("match_weights") or DEFAULT_MATCH_WEIGHTS)
    denominator = sum(max(0.0, float(weight)) for weight in selected_weights.values())
    if denominator <= 0:
        return None

    numerator = 0.0
    for field, weight in selected_weights.items():
        numerator += _clamp01(match.get(field)) * max(0.0, float(weight))

    return round(numerator / denominator, 4)


def evidence_priority(item: Mapping[str, Any], match_score: Optional[float] = None) -> int:
    """Return pricing priority where 1 is the strongest budget anchor."""
    source_type = str(item.get("source_type", "")).strip().lower()
    current = bool(item.get("quote_current", False))
    comparable = bool(item.get("comparable", False))
    score = match_score if match_score is not None else configuration_match_score(item)

    if current and score is not None and score >= 0.95 and source_type in FORMAL_CURRENT_SOURCES:
        return 1
    if current and score is not None and score >= 0.95 and source_type in CURRENT_MARKET_SOURCES:
        return 2
    if current and score is not None and score >= 0.85 and comparable:
        return 3
    if source_type in HISTORICAL_SOURCES and comparable and (score is None or score >= 0.85):
        return 4
    if source_type in COMPONENT_SOURCES:
        return 5
    if source_type in GENERIC_SOURCES:
        return 6
    if source_type in ESTIMATE_SOURCES:
        return 7

    # Legacy/current comparable evidence without an explicit match score is
    # deliberately kept below exact-config evidence.
    if current and comparable:
        return 3 if score is not None and score >= 0.85 else 6
    return 7


def normalize(items: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    for item in items:
        row = dict(item)
        score = configuration_match_score(item)
        priority = evidence_priority(item, score)
        row["normalized_comparable_cost"] = round(normalized_cost(item), 2)
        row["configuration_match_score"] = score
        row["exact_configuration_match"] = bool(score is not None and score >= 0.95)
        row["highly_comparable_configuration"] = bool(score is not None and score >= 0.85)
        row["evidence_priority"] = priority

        missing = []
        for key in ("configuration", "source_type", "source_date"):
            if not item.get(key):
                missing.append(key)

        match_usable = score is None or score >= 0.70
        row["comparison_ready"] = bool(item.get("comparable", False)) and not missing and match_usable
        row["match_assessment_missing"] = score is None
        row["missing_fields"] = missing
        output.append(row)
    return output


def select_budget_anchor(items: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Select the strongest evidence tier without blending weaker prices into it."""
    rows = normalize(items)
    usable = [
        row
        for row in rows
        if row["comparison_ready"] and float(row["normalized_comparable_cost"]) > 0
    ]

    if not usable:
        return {
            "status": "needs-confirmation",
            "reason": "No comparison-ready price evidence",
            "recommended_budget_low": None,
            "recommended_budget_high": None,
            "confidence": "Needs confirmation",
        }

    best_priority = min(int(row["evidence_priority"]) for row in usable)
    anchors = [row for row in usable if int(row["evidence_priority"]) == best_priority]
    costs = sorted(float(row["normalized_comparable_cost"]) for row in anchors)

    exact_current = best_priority in (1, 2)
    if exact_current and len(anchors) >= 2:
        confidence = "Market-verified / Exact-config"
        needs_second_quote = False
    elif exact_current:
        confidence = "Verified current quote / Exact-config"
        needs_second_quote = True
    elif best_priority == 3:
        confidence = "Market-verified / Highly-matched"
        needs_second_quote = True
    elif best_priority == 4:
        confidence = "Comparable-transaction"
        needs_second_quote = True
    else:
        confidence = "Estimated"
        needs_second_quote = True

    historical_context = sorted(
        float(row["normalized_comparable_cost"])
        for row in usable
        if int(row["evidence_priority"]) == 4
    )

    return {
        "status": "ready",
        "preferred_evidence_priority": best_priority,
        "anchor_count": len(anchors),
        "recommended_budget_low": round(costs[0], 2),
        "recommended_budget_high": round(costs[-1], 2),
        "confidence": confidence,
        "needs_second_quote": needs_second_quote,
        "lower_priority_evidence_excluded_from_anchor": len(usable) - len(anchors),
        "historical_context_low": round(historical_context[0], 2) if historical_context else None,
        "historical_context_high": round(historical_context[-1], 2) if historical_context else None,
        "rule": "Lower-priority evidence is context only and is not averaged into the preferred budget anchor.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize and rank procurement price evidence")
    parser.add_argument("input", type=Path, help="JSON file containing an array or {'items': [...]} object")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Include the preferred budget anchor selected by evidence priority",
    )
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    rows = normalize(items)

    if args.summary:
        result: Any = {"items": rows, "budget_anchor": select_budget_anchor(items)}
    else:
        result = rows
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

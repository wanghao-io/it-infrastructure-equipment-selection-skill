#!/usr/bin/env python3
"""Normalize and rank procurement price evidence.

Core pricing rules:
- current exact-configuration quotations outrank lower-match historical/generic prices;
- search-channel prestige does not override configuration match;
- user/project-saved human quotations can be strong evidence when source/date/scope are captured;
- misleading base/start prices and unavailable configurations are excluded from the
  primary budget anchor but retained as contextual evidence;
- weak evidence cannot silently justify a downward revision of an existing
  configurable-enterprise budget.
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
    "manufacturer-customer-service-quote",
    "official-brand-store-human-quote",
    "official-store-human-quote",
    "official-store-quote",
    "authorized-reseller-quote",
    "authorized-channel-quote",
    "user-provided-current-quote",
    "project-saved-current-quote",
    "project-quote-record",
    # legacy names kept for compatibility
    "official-quote",
    "authorized-channel",
}

CURRENT_MARKET_SOURCES = {
    "enterprise-marketplace-quote",
    "enterprise-marketplace-exact-sku",
    "official-marketplace-exact-sku",
    "market-aggregator-verified-quote",
    "retail-exact-quote",
    "retail-exact-sku",
    # legacy
    "enterprise-marketplace",
}

HISTORICAL_SOURCES = {"government-award", "public-procurement-award"}
COMPONENT_SOURCES = {"component-estimate", "component-cost-model"}
GENERIC_SOURCES = {
    "generic-listing",
    "retail",
    "model-family-listing",
    "market-aggregator",
    "price-history",
    "deal-community",
}
ESTIMATE_SOURCES = {"engineering-estimate", "estimate"}
CONTEXT_ONLY_SOURCES = {"market-aggregator", "price-history", "deal-community"}

MISLEADING_QUOTE_MODES = {"starting-price", "base-config-listing", "generic-listing"}


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

    Explicit ``configuration_match_score`` or ``exact_configuration_match`` may
    be used when the caller already performed a device-specific match. Otherwise
    the default server-oriented weighted field model is used. Missing fields are
    treated as unknown/non-matching, not silently as 1.0.
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

    # Aggregators/history/deal communities are context sources unless the record
    # is explicitly represented as a verified quote/SKU source above.
    if source_type in CONTEXT_ONLY_SOURCES:
        return 6

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

    # Legacy/current comparable evidence without explicit source typing stays
    # below exact-config evidence.
    if current and comparable:
        return 3 if score is not None and score >= 0.85 else 6
    return 7


def anchor_exclusion_reasons(item: Mapping[str, Any], match_score: Optional[float]) -> List[str]:
    """Explain why a price signal must not become a primary budget anchor."""
    reasons: List[str] = []
    product_class = str(item.get("product_class", "")).strip().lower()
    quote_mode = str(item.get("quote_mode", "")).strip().lower()

    if not item.get("comparable", False):
        reasons.append("not-marked-comparable")
    if match_score is not None and match_score < 0.70:
        reasons.append("configuration-match-below-0.70")
    if item.get("starting_price_or_base_config") is True:
        reasons.append("starting-or-base-configuration-price")
    if quote_mode in MISLEADING_QUOTE_MODES:
        reasons.append(f"quote-mode:{quote_mode}")
    if product_class == "configurable-enterprise" and quote_mode in MISLEADING_QUOTE_MODES:
        reasons.append("configurable-enterprise-requires-config-level-price")
    if item.get("orderability_confirmed") is False:
        reasons.append("orderability-not-confirmed")
    if item.get("used_or_refurbished") is True and not item.get("used_allowed", False):
        reasons.append("used-or-refurbished-not-allowed")
    if item.get("price_scope_complete") is False:
        reasons.append("commercial-scope-incomplete")

    return reasons


def price_signal_role(priority: int) -> str:
    return {
        1: "primary-current-formal-quote",
        2: "primary-current-market-quote",
        3: "secondary-current-comparable",
        4: "historical-comparable-or-fallback",
        5: "component-cost-fallback",
        6: "weak-market-context",
        7: "engineering-estimate",
    }.get(priority, "unknown")


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
        row["price_signal_role"] = price_signal_role(priority)

        missing = []
        for key in ("configuration", "source_type", "source_date"):
            if not item.get(key):
                missing.append(key)

        match_usable = score is None or score >= 0.70
        row["comparison_ready"] = bool(item.get("comparable", False)) and not missing and match_usable
        exclusions = anchor_exclusion_reasons(item, score)
        row["anchor_exclusion_reasons"] = exclusions
        row["anchor_eligible"] = bool(row["comparison_ready"] and not exclusions)
        row["match_assessment_missing"] = score is None
        row["missing_fields"] = missing
        output.append(row)
    return output


def select_budget_anchor(items: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Select the strongest eligible evidence tier without blending weaker prices."""
    rows = normalize(items)
    eligible = [
        row
        for row in rows
        if row["anchor_eligible"] and float(row["normalized_comparable_cost"]) > 0
    ]

    if not eligible:
        return {
            "status": "needs-confirmation",
            "reason": "No anchor-eligible price evidence",
            "recommended_budget_low": None,
            "recommended_budget_high": None,
            "confidence": "Needs confirmation",
            "confidence_level": "Low",
            "excluded_signal_count": len([row for row in rows if row["anchor_exclusion_reasons"]]),
        }

    best_priority = min(int(row["evidence_priority"]) for row in eligible)
    anchors = [row for row in eligible if int(row["evidence_priority"]) == best_priority]
    costs = sorted(float(row["normalized_comparable_cost"]) for row in anchors)

    exact_current = best_priority in (1, 2)
    if exact_current and len(anchors) >= 2:
        confidence = "Market-verified / Exact-config"
        confidence_level = "High"
        needs_second_quote = False
    elif exact_current:
        confidence = "Verified current quote / Exact-config"
        confidence_level = "Medium"
        needs_second_quote = True
    elif best_priority == 3:
        confidence = "Market-verified / Highly-matched"
        confidence_level = "Medium"
        needs_second_quote = True
    elif best_priority == 4:
        confidence = "Comparable-transaction"
        confidence_level = "Low"
        needs_second_quote = True
    elif best_priority == 5:
        confidence = "Estimated / Component-model"
        confidence_level = "Low"
        needs_second_quote = True
    else:
        confidence = "Estimated"
        confidence_level = "Low"
        needs_second_quote = True

    historical_context = sorted(
        float(row["normalized_comparable_cost"])
        for row in rows
        if row["comparison_ready"]
        and int(row["evidence_priority"]) == 4
        and float(row["normalized_comparable_cost"]) > 0
    )

    return {
        "status": "ready",
        "preferred_evidence_priority": best_priority,
        "anchor_count": len(anchors),
        "anchor_candidates": [row.get("candidate") for row in anchors],
        "recommended_budget_low": round(costs[0], 2),
        "recommended_budget_high": round(costs[-1], 2),
        "confidence": confidence,
        "confidence_level": confidence_level,
        "needs_second_quote": needs_second_quote,
        "lower_priority_evidence_excluded_from_anchor": len(eligible) - len(anchors),
        "excluded_signal_count": len([row for row in rows if row["anchor_exclusion_reasons"]]),
        "historical_context_low": round(historical_context[0], 2) if historical_context else None,
        "historical_context_high": round(historical_context[-1], 2) if historical_context else None,
        "rule": "Lower-priority or misleading evidence is context only and is not averaged into the preferred budget anchor.",
    }


def _infer_product_class(rows: Iterable[Mapping[str, Any]], explicit: Optional[str]) -> str:
    if explicit:
        return explicit.strip().lower()
    for row in rows:
        value = str(row.get("product_class", "")).strip().lower()
        if value:
            return value
    return ""


def assess_budget_revision(
    existing_budget: float,
    items: Iterable[Mapping[str, Any]],
    *,
    product_class: Optional[str] = None,
) -> Dict[str, Any]:
    """Assess whether current evidence can safely revise an existing unit budget.

    For configurable-enterprise equipment, weak/context evidence may inform risk
    commentary but cannot by itself justify a downward budget revision.
    """
    item_list = list(items)
    rows = normalize(item_list)
    anchor = select_budget_anchor(item_list)
    existing = round(_number(existing_budget), 2)
    inferred_class = _infer_product_class(rows, product_class)

    if existing <= 0:
        return {
            "decision": "no-existing-budget",
            "product_class": inferred_class,
            "existing_budget": existing,
            "budget_anchor": anchor,
        }

    if anchor.get("status") != "ready":
        return {
            "decision": "hold-existing-provisional",
            "product_class": inferred_class,
            "existing_budget": existing,
            "recommended_budget_low": existing,
            "recommended_budget_high": existing,
            "confidence": "Needs confirmation",
            "reason": "No strong current anchor is available; keep the prior amount only as a provisional carry-forward.",
            "budget_anchor": anchor,
        }

    low = float(anchor["recommended_budget_low"])
    high = float(anchor["recommended_budget_high"])
    priority = int(anchor["preferred_evidence_priority"])
    anchor_count = int(anchor.get("anchor_count", 0))

    strong_for_downward_revision = priority in (1, 2) or (priority == 3 and anchor_count >= 2)
    proposes_downward_revision = high < existing

    if inferred_class == "configurable-enterprise" and proposes_downward_revision and not strong_for_downward_revision:
        return {
            "decision": "hold-existing-provisional",
            "product_class": inferred_class,
            "existing_budget": existing,
            "recommended_budget_low": existing,
            "recommended_budget_high": existing,
            "confidence": "Needs confirmation",
            "reason": (
                "Weak/partial evidence cannot justify lowering an existing configurable-enterprise budget. "
                "Require at least one exact-current Tier 1/2 quote or two independent Tier 3 highly matched quotes."
            ),
            "rejected_anchor_low": round(low, 2),
            "rejected_anchor_high": round(high, 2),
            "budget_anchor": anchor,
        }

    return {
        "decision": "revise-to-current-anchor" if (low != existing or high != existing) else "keep-current-anchor",
        "product_class": inferred_class,
        "existing_budget": existing,
        "recommended_budget_low": round(low, 2),
        "recommended_budget_high": round(high, 2),
        "confidence": anchor.get("confidence"),
        "reason": "Current evidence is strong enough for the proposed revision direction.",
        "budget_anchor": anchor,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize and rank procurement price evidence")
    parser.add_argument("input", type=Path, help="JSON file containing an array or {'items': [...]} object")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Include the preferred budget anchor selected by evidence priority",
    )
    parser.add_argument(
        "--existing-budget",
        type=float,
        help="Existing unit budget to evaluate against current evidence",
    )
    parser.add_argument(
        "--product-class",
        help="Optional product class override, e.g. configurable-enterprise",
    )
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    rows = normalize(items)

    if args.summary:
        result: Any = {"items": rows, "budget_anchor": select_budget_anchor(items)}
        if args.existing_budget is not None:
            result["budget_revision"] = assess_budget_revision(
                args.existing_budget,
                items,
                product_class=args.product_class,
            )
    else:
        result = rows
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

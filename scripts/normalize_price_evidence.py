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
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from contracts import (
    is_unresolved,
    require_bool,
    require_currency,
    require_float,
    require_iso_date,
    strict_json_dumps,
    strict_json_loads,
)
from validate_json_schemas import validate_file


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
COMMERCIAL_COST_FIELDS = (
    "mandatory_accessories",
    "required_licenses",
    "warranty_support",
    "required_implementation",
    "tax_amount",
    "shipping",
)


def _clamp01(value: Any) -> float:
    return require_float(value, "configuration match", minimum=0, maximum=1)


def normalized_cost(item: Mapping[str, Any]) -> float:
    """Return project-comparable cost using all disclosed commercial scope."""
    base_value = item.get("hardware_price", item.get("price"))
    base = require_float(base_value, "hardware_price/price", minimum=0)
    total = base
    for field in COMMERCIAL_COST_FIELDS:
        value = item.get(field, 0)
        total += require_float(value, field, minimum=0)
    return total


def invalid_commercial_fields(item: Mapping[str, Any]) -> list[str]:
    invalid: list[str] = []
    base_value = item.get("hardware_price", item.get("price"))
    try:
        require_float(base_value, "hardware_price/price", minimum=0)
    except (TypeError, ValueError):
        invalid.append("hardware_price/price")
    for field in COMMERCIAL_COST_FIELDS:
        if field in item:
            try:
                require_float(item[field], field, minimum=0)
            except (TypeError, ValueError):
                invalid.append(field)
    return invalid


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
    current = require_bool(item.get("quote_current", False), "quote_current")
    comparable = require_bool(item.get("comparable", False), "comparable")
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

    comparable = require_bool(item.get("comparable", False), "comparable")
    if not comparable:
        reasons.append("not-marked-comparable")
    if match_score is not None and match_score < 0.70:
        reasons.append("configuration-match-below-0.70")
    if item.get("starting_price_or_base_config") is True:
        reasons.append("starting-or-base-configuration-price")
    if quote_mode in MISLEADING_QUOTE_MODES:
        reasons.append(f"quote-mode:{quote_mode}")
    if product_class == "configurable-enterprise" and quote_mode in MISLEADING_QUOTE_MODES:
        reasons.append("configurable-enterprise-requires-config-level-price")
    # Fail closed for every product class.  A price is never an anchor until a
    # separate technical assessment explicitly passes it for pricing.
    if item.get("technical_fit_status") != "PASS":
        reasons.append("technical-fit-not-pass")
    if item.get("eligible_for_pricing") is not True:
        reasons.append("technical-fit-not-eligible-for-pricing")
    if item.get("orderability_confirmed") is False:
        reasons.append("orderability-not-confirmed")
    if item.get("used_or_refurbished") is True and not item.get("used_allowed", False):
        reasons.append("used-or-refurbished-not-allowed")
    if item.get("price_scope_complete") is False:
        reasons.append("commercial-scope-incomplete")

    priority = evidence_priority(item, match_score)
    if product_class == "configurable-enterprise" and priority in (1, 2, 3):
        if item.get("technical_fit_status") != "PASS" or item.get("eligible_for_pricing") is not True:
            reasons.append("configurable-enterprise-technical-fit-unverified")
        if item.get("orderability_confirmed") is not True:
            reasons.append("configurable-enterprise-orderability-unverified")
        if item.get("price_scope_complete") is not True:
            reasons.append("configurable-enterprise-commercial-scope-unverified")
        for field in COMMERCIAL_COST_FIELDS:
            if field not in item:
                reasons.append(f"missing-commercial-field:{field}")
        if "tax_included" not in item or type(item.get("tax_included")) is not bool:
            reasons.append("missing-or-invalid-tax-included")

    if item.get("source_date"):
        source_date = require_iso_date(item["source_date"], "source_date")
        if require_bool(item.get("quote_current", False), "quote_current"):
            as_of = require_iso_date(item.get("as_of_date", date.today().isoformat()), "as_of_date")
            max_age_days = require_float(item.get("max_quote_age_days", 90), "max_quote_age_days", minimum=0)
            age_days = (as_of - source_date).days
            if age_days < 0:
                reasons.append("quote-date-in-future")
            elif age_days > max_age_days:
                reasons.append("quote-stale")
    if item.get("quote_valid_until"):
        valid_until = require_iso_date(item["quote_valid_until"], "quote_valid_until")
        as_of = require_iso_date(item.get("as_of_date", date.today().isoformat()), "as_of_date")
        if valid_until < as_of:
            reasons.append("quote-expired")
    if item.get("currency"):
        require_currency(item["currency"])
    reasons.extend(f"invalid-commercial-field:{field}" for field in invalid_commercial_fields(item))

    return list(dict.fromkeys(reasons))


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
        if "evidence_level" in row:
            row["declared_evidence_level"] = row.pop("evidence_level")
        score = configuration_match_score(item)
        priority = evidence_priority(item, score)
        try:
            cost = round(normalized_cost(item), 2)
        except (TypeError, ValueError):
            cost = None
        row["normalized_comparable_cost"] = cost
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
        comparable = require_bool(item.get("comparable", False), "comparable")
        row["comparison_ready"] = comparable and not missing and match_usable
        exclusions = anchor_exclusion_reasons(item, score)
        row["anchor_exclusion_reasons"] = exclusions
        row["anchor_eligible"] = bool(row["comparison_ready"] and not exclusions)
        if not row["anchor_eligible"]:
            row["derived_evidence_level"] = "Needs confirmation"
        elif priority in (1, 2, 3):
            row["derived_evidence_level"] = "Market-verified"
        elif priority == 4:
            row["derived_evidence_level"] = "Comparable-transaction"
        else:
            row["derived_evidence_level"] = "Estimated"
        row["match_assessment_missing"] = score is None
        row["missing_fields"] = missing
        output.append(row)
    return output


def select_budget_anchor(items: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Select the strongest eligible evidence tier without blending weaker prices."""
    rows = normalize(items)
    try:
        product_class = _infer_product_class(rows, None)
    except ValueError as exc:
        return {
            "status": "needs-confirmation",
            "reason": str(exc),
            "recommended_budget_low": None,
            "recommended_budget_high": None,
            "confidence": "Needs confirmation",
            "confidence_level": "Low",
        }
    scopes = {str(row.get("decision_scope_id", "")).strip() for row in rows}
    if len(scopes) > 1:
        return {
            "status": "needs-confirmation",
            "reason": "Price evidence from different decision_scope_id values must not be aggregated.",
            "recommended_budget_low": None,
            "recommended_budget_high": None,
            "confidence": "Needs confirmation",
            "confidence_level": "Low",
            "decision_scopes": sorted(scopes),
        }
    eligible = [
        row
        for row in rows
        if row["anchor_eligible"]
        and row["normalized_comparable_cost"] is not None
        and float(row["normalized_comparable_cost"]) > 0
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
    candidate_anchors = [row for row in eligible if int(row["evidence_priority"]) == best_priority]
    currencies = {str(row.get("currency", "")).upper() for row in candidate_anchors}
    if "" in currencies or len(currencies) != 1:
        return {
            "status": "needs-confirmation",
            "reason": "Anchor-eligible evidence must use one explicit currency; convert externally before comparison.",
            "recommended_budget_low": None,
            "recommended_budget_high": None,
            "confidence": "Needs confirmation",
            "confidence_level": "Low",
            "currencies": sorted(currencies),
        }

    anchors_by_source: Dict[str, Dict[str, Any]] = {}
    for row in candidate_anchors:
        supplier = " ".join(str(row.get("supplier", "")).split()).casefold()
        channel = " ".join(str(row.get("sales_channel", "")).split()).casefold()
        source = " ".join(str(row.get("source", "")).split()).casefold()
        # Quote numbers are records, not independent market sources.  Count a
        # supplier/channel once; for web evidence use seller/source identity.
        identity = ("supplier", supplier, channel) if supplier else (
            "source", source, channel, str(row.get("source_type", "")).casefold()
        )
        identity_key = json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str)
        current = anchors_by_source.get(identity_key)
        # A supplier may issue revisions under different quote IDs.  Select the
        # newest eligible record; when dates tie, prefer complete commercial
        # scope and then the conservative higher comparable cost.  The final
        # anchor must not depend on input ordering.
        selection_key = (
            str(row.get("source_date", "")),
            bool(row.get("price_scope_complete") is True),
            float(row["normalized_comparable_cost"]),
            json.dumps(
                (row.get("candidate"), row.get("quote_id"), row.get("source")),
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            ),
        )
        if current is None or selection_key > current["selection_key"]:
            anchors_by_source[identity_key] = {"selection_key": selection_key, "row": row}
    anchors = [anchors_by_source[key]["row"] for key in sorted(anchors_by_source)]
    costs = sorted(float(row["normalized_comparable_cost"]) for row in anchors)

    exact_current = best_priority in (1, 2)
    if exact_current and len(anchors) >= 2:
        confidence = "Market-verified / Exact-config"
        confidence_level = "High"
        needs_second_quote = False
    elif exact_current:
        confidence = "Market-verified / Exact-config"
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
        and row["normalized_comparable_cost"] is not None
        and float(row["normalized_comparable_cost"]) > 0
    )

    return {
        "status": "ready",
        "product_class": product_class,
        "preferred_evidence_priority": best_priority,
        "anchor_count": len(anchors),
        "currency": next(iter(currencies)),
        "anchor_candidates": [row.get("candidate") for row in anchors],
        "recommended_budget_low": round(costs[0], 2),
        "recommended_budget_high": round(costs[-1], 2),
        "confidence": confidence,
        "confidence_level": confidence_level,
        "needs_second_quote": needs_second_quote,
        "lower_priority_evidence_excluded_from_anchor": len([
            row for row in rows
            if row.get("comparison_ready") and int(row.get("evidence_priority", 99)) > best_priority
        ]),
        "excluded_signal_count": len([row for row in rows if row["anchor_exclusion_reasons"]]),
        "historical_context_low": round(historical_context[0], 2) if historical_context else None,
        "historical_context_high": round(historical_context[-1], 2) if historical_context else None,
        "rule": "Lower-priority or misleading evidence is context only and is not averaged into the preferred budget anchor.",
    }


def _infer_product_class(rows: Iterable[Mapping[str, Any]], explicit: Optional[str]) -> str:
    allowed = {"configurable-enterprise", "fixed-sku", "commodity-component"}
    classes = {
        str(row.get("product_class", "")).strip().lower()
        for row in rows
        if str(row.get("product_class", "")).strip()
    }
    if len(classes) > 1:
        raise ValueError(
            "Price evidence with different product_class values must not share one decision scope."
        )
    declared = explicit.strip().lower() if explicit else ""
    if declared and declared not in allowed:
        raise ValueError(f"Unsupported product_class: {declared}")
    if classes - allowed:
        raise ValueError(f"Unsupported evidence product_class: {', '.join(sorted(classes - allowed))}")
    if declared and classes and declared not in classes:
        raise ValueError(
            "The product_class override conflicts with the evidence product_class and cannot change decision policy."
        )
    return declared or (next(iter(classes)) if classes else "")


def assess_budget_revision(
    existing_budget: float,
    items: Iterable[Mapping[str, Any]],
    *,
    product_class: Optional[str] = None,
    existing_currency: Optional[str] = None,
) -> Dict[str, Any]:
    """Assess whether current evidence can safely revise an existing unit budget.

    For configurable-enterprise equipment, weak/context evidence may inform risk
    commentary but cannot by itself justify a downward budget revision.
    """
    item_list = list(items)
    rows = normalize(item_list)
    anchor = select_budget_anchor(item_list)
    existing = round(require_float(existing_budget, "existing_budget", minimum=0), 2)
    try:
        inferred_class = _infer_product_class(rows, product_class)
    except ValueError as exc:
        return {
            "decision": "hold-existing-provisional",
            "product_class": "",
            "existing_budget": existing,
            "recommended_budget_low": existing,
            "recommended_budget_high": existing,
            "confidence": "Needs confirmation",
            "reason": str(exc),
            "budget_anchor": anchor,
        }

    if existing <= 0:
        return {
            "decision": "no-existing-budget",
            "product_class": inferred_class,
            "existing_budget": existing,
            "budget_anchor": anchor,
        }

    if anchor.get("status") != "ready":
        reason = (
            "No strong current anchor with explicit PASS technical fit and eligible_for_pricing=true is available; "
            "keep the prior amount only as a provisional carry-forward."
        )
        if inferred_class == "configurable-enterprise":
            reason += " Incomplete or unverified evidence cannot justify lowering this configurable-enterprise budget."
        return {
            "decision": "hold-existing-provisional",
            "product_class": inferred_class,
            "existing_budget": existing,
            "recommended_budget_low": existing,
            "recommended_budget_high": existing,
            "confidence": "Needs confirmation",
            "reason": reason,
            "budget_anchor": anchor,
        }

    if not existing_currency:
        return {
            "decision": "hold-existing-provisional",
            "product_class": inferred_class,
            "existing_budget": existing,
            "recommended_budget_low": existing,
            "recommended_budget_high": existing,
            "confidence": "Needs confirmation",
            "reason": "Existing budget currency is required before comparing it with current evidence.",
            "budget_anchor": anchor,
        }
    baseline_currency = require_currency(existing_currency, "existing_currency")
    if baseline_currency != anchor.get("currency"):
        return {
            "decision": "hold-existing-provisional",
            "product_class": inferred_class,
            "existing_budget": existing,
            "existing_currency": baseline_currency,
            "recommended_budget_low": existing,
            "recommended_budget_high": existing,
            "confidence": "Needs confirmation",
            "reason": "Existing budget and current evidence currencies differ; convert with an explicit dated basis before revision.",
            "budget_anchor": anchor,
        }

    low = float(anchor["recommended_budget_low"])
    high = float(anchor["recommended_budget_high"])
    priority = int(anchor["preferred_evidence_priority"])
    anchor_count = int(anchor.get("anchor_count", 0))

    strong_for_downward_revision = priority in (1, 2) or (priority == 3 and anchor_count >= 2)
    # A range whose lower bound is below the current budget still authorizes a
    # possible reduction.  Gate that case even when the upper bound overlaps
    # or exceeds the existing amount.
    proposes_downward_revision = low < existing

    if proposes_downward_revision:
        anchor_rows = [
            row for row in rows
            if row.get("anchor_eligible")
            and int(row.get("evidence_priority", 99)) == priority
            and str(row.get("currency", "")).upper() == anchor.get("currency")
        ]
        technical_fit_verified = bool(anchor_rows) and all(
            row.get("technical_fit_status") == "PASS" and row.get("eligible_for_pricing") is True
            for row in anchor_rows
        )
        if not technical_fit_verified:
            return {
                "decision": "hold-existing-provisional",
                "product_class": inferred_class,
                "existing_budget": existing,
                "recommended_budget_low": existing,
                "recommended_budget_high": existing,
                "confidence": "Needs confirmation",
                "reason": "A downward revision requires explicit PASS technical fit and eligible_for_pricing=true for every anchor, regardless of product class.",
                "rejected_anchor_low": round(low, 2),
                "rejected_anchor_high": round(high, 2),
                "budget_anchor": anchor,
            }

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
        "existing_currency": baseline_currency,
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
    parser.add_argument(
        "--existing-currency",
        help="Three-letter currency code for --existing-budget; required for a revision decision",
    )
    contract_group = parser.add_mutually_exclusive_group()
    contract_group.add_argument(
        "--strict-contract",
        action="store_true",
        help="Validate the versioned JSON envelope before making a pricing decision",
    )
    contract_group.add_argument(
        "--legacy-input",
        action="store_true",
        help="Explicitly allow an unversioned object or bare array (deprecated)",
    )
    args = parser.parse_args()

    data = strict_json_loads(args.input.read_text(encoding="utf-8"))
    if args.strict_contract:
        if not isinstance(data, dict) or "schema_version" not in data:
            raise SystemExit("$: strict contract requires a versioned object envelope")
        version = data.get("schema_version")
        schema_path = Path(__file__).resolve().parents[1] / (
            "schemas/price-evidence.schema.json" if version == 1
            else "schemas/v2/price-evidence.schema.json" if version == 2
            else f"schemas/unsupported-price-evidence-v{version}.schema.json"
        )
        if not schema_path.is_file():
            raise SystemExit(f"$.schema_version: unsupported price-evidence version {version!r}")
        errors = validate_file(schema_path, args.input)
        if errors:
            raise SystemExit("\n".join(errors))
    elif not isinstance(data, dict) or "schema_version" not in data:
        if not args.legacy_input:
            raise SystemExit(
                "$: unversioned price input is deprecated; use --strict-contract with a versioned envelope "
                "or explicitly pass --legacy-input"
            )
        print("WARNING: legacy unversioned price input; no schema preflight was performed", file=__import__("sys").stderr)
    items = data["items"] if isinstance(data, dict) else data
    if isinstance(data, dict) and data.get("decision_scope_id"):
        items = [{**item, "decision_scope_id": data["decision_scope_id"]} for item in items]
    rows = normalize(items)

    if args.summary:
        result: Any = {"items": rows, "budget_anchor": select_budget_anchor(items)}
        if args.existing_budget is not None:
            if not args.existing_currency:
                raise SystemExit("--existing-currency is required with --existing-budget")
            result["budget_revision"] = assess_budget_revision(
                args.existing_budget,
                items,
                product_class=args.product_class,
                existing_currency=args.existing_currency,
            )
    else:
        result = rows
    print(strict_json_dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

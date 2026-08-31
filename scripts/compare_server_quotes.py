#!/usr/bin/env python3
"""Create a budget control range from validated, independent server quotes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any

from validate_server_quote import validate_quote
from contracts import require_float, strict_json_dumps, strict_json_loads
from validate_json_schemas import validate_file


def compare(
    requirement: dict[str, Any], quotes: list[dict[str, Any]], *, contract_version: int = 1
) -> dict[str, Any]:
    validated = [
        (q, validate_quote(requirement, q, contract_version=contract_version)) for q in quotes
    ]
    eligible = [(q, v) for q, v in validated if v["eligible_for_pricing"]]
    currencies = {v["currency"] for _, v in eligible}
    if not eligible:
        return {"status": "needs-confirmation", "reason": "No technically and commercially valid quote", "quotes": [v for _, v in validated]}
    if len(currencies) != 1:
        return {"status": "needs-confirmation", "reason": "Mixed currencies require an explicit conversion basis", "currencies": sorted(currencies)}
    if contract_version >= 2:
        commercial_scopes = {
            str(q.get("commercial_scope_id", "")).strip() for q, _ in eligible
        }
        if "" in commercial_scopes or len(commercial_scopes) != 1:
            return {
                "status": "needs-confirmation",
                "reason": "Eligible quotations must share one explicit commercial_scope_id.",
                "commercial_scope_ids": sorted(commercial_scopes),
            }
        # Scope identifiers are labels, not commercial evidence. Conservatively
        # refuse differences until a separate, documented normalization is made.
        bases = {
            (q["tax_included"],
             " ".join(q["tax_basis"].casefold().split()),
             " ".join(q["delivery_basis"].casefold().split()))
            for q, _ in eligible
        }
        if len(bases) != 1:
            return {
                "status": "needs-confirmation",
                "reason": "Tax/delivery bases differ; commercial_scope_id cannot normalize them.",
                "quotes": [v for _, v in validated],
            }

    independent = {}
    for quote, result in eligible:
        supplier_identity = " ".join(str(quote["supplier"]).strip().casefold().split())
        previous = independent.get(supplier_identity)
        selection_key = (
            str(result.get("source_date", "")),
            float(result["normalized_comparable_cost"]),
            str(result.get("quote_id", "")),
        )
        previous_key = (
            str(previous.get("source_date", "")),
            float(previous["normalized_comparable_cost"]),
            str(previous.get("quote_id", "")),
        ) if previous else None
        if previous is None or selection_key > previous_key:
            independent[supplier_identity] = result
    costs = sorted(float(row["normalized_comparable_cost"]) for row in independent.values())
    if contract_version == 1:
        confidence = "Medium"
        action = "V1 validates only coarse minimum fields. Reissue the RFQ under server-rfq-v2 before any exact-configuration or High-confidence claim."
    elif len(costs) < 2:
        confidence = "Medium"
        action = "Obtain a second independent, exact-configuration quote before reducing budget."
    else:
        confidence = "High"
        action = "Use the range as the procurement control band; retain explicit contingency for delivery risk."
    reserve_percent = require_float(requirement.get("risk_reserve_percent", 0), "risk_reserve_percent", minimum=0, maximum=100)
    control_high = max(costs) * (1 + reserve_percent / 100)
    return {
        "status": "ready",
        "currency": next(iter(currencies)),
        "independent_quote_count": len(costs),
        "market_low": round(min(costs), 2),
        "negotiation_target": round(median(costs), 2),
        "market_high": round(max(costs), 2),
        "budget_control_high": round(control_high, 2),
        "risk_reserve_percent": reserve_percent,
        "confidence_level": confidence,
        "configuration_match_level": "exact-procurement-object" if contract_version >= 2 else "coarse-minimum",
        "contract_version": contract_version,
        "comparison_scope": "declared RFQ configuration and commercial basis only; verify external evidence separately",
        "action": action,
        "quotes": [v for _, v in validated],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare validated server quotations")
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    data = strict_json_loads(args.input.read_text(encoding="utf-8"))
    version = data.get("schema_version") if isinstance(data, dict) else None
    schema_path = Path(__file__).resolve().parents[1] / (
        "schemas/server-rfq.schema.json" if version == 1
        else "schemas/v2/server-rfq.schema.json" if version == 2
        else f"schemas/unsupported-server-rfq-v{version}.schema.json"
    )
    if not schema_path.is_file():
        raise SystemExit(f"$.schema_version: unsupported server-rfq version {version!r}")
    errors = validate_file(schema_path, args.input)
    if errors:
        raise SystemExit("\n".join(errors))
    print(strict_json_dumps(compare(data["requirement"], data["quotes"], contract_version=version), ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

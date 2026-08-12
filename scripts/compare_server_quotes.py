#!/usr/bin/env python3
"""Create a budget control range from validated, independent server quotes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any

from validate_server_quote import validate_quote
from contracts import require_float


def compare(requirement: dict[str, Any], quotes: list[dict[str, Any]]) -> dict[str, Any]:
    validated = [(q, validate_quote(requirement, q)) for q in quotes]
    eligible = [(q, v) for q, v in validated if v["eligible_for_pricing"]]
    currencies = {v["currency"] for _, v in eligible}
    if not eligible:
        return {"status": "needs-confirmation", "reason": "No technically and commercially valid quote", "quotes": [v for _, v in validated]}
    if len(currencies) != 1:
        return {"status": "needs-confirmation", "reason": "Mixed currencies require an explicit conversion basis", "currencies": sorted(currencies)}

    independent = {}
    for quote, result in eligible:
        supplier_identity = " ".join(str(quote["supplier"]).strip().casefold().split())
        previous = independent.get(supplier_identity)
        if previous is None or float(result["normalized_comparable_cost"]) > float(previous["normalized_comparable_cost"]):
            independent[supplier_identity] = result
    costs = sorted(float(row["normalized_comparable_cost"]) for row in independent.values())
    if len(costs) < 2:
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
        "action": action,
        "quotes": [v for _, v in validated],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare validated server quotations")
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(compare(data["requirement"], data["quotes"]), ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

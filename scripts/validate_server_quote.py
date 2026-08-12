#!/usr/bin/env python3
"""Validate server quotations against a frozen RFQ baseline."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from contracts import is_unresolved, require_bool, require_currency, require_decimal, require_float, require_iso_date

COST_FIELDS = (
    "hardware_price", "mandatory_accessories", "required_licenses",
    "warranty_support", "required_implementation", "tax_amount", "shipping",
)
REQUIRED_CONFIGURATION_FIELDS = {
    "cpu_cores", "memory_gb", "usable_storage_tb", "raid_cache_with_plp",
    "network_ports_10gbe", "redundant_power", "warranty_years",
}


def _equivalent(actual: Any, expected: Any) -> bool:
    if type(expected) is bool:
        return type(actual) is bool and actual is expected
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        try:
            return Decimal(str(actual)) >= Decimal(str(expected))
        except Exception:
            return False
    if isinstance(expected, list):
        return all(value in (actual if isinstance(actual, list) else [actual]) for value in expected)
    return str(actual).strip().casefold() == str(expected).strip().casefold()


def validate_quote(requirement: dict[str, Any], quote: dict[str, Any]) -> dict[str, Any]:
    required = requirement.get("required_configuration", {})
    if not isinstance(required, dict) or not required:
        raise ValueError("required_configuration must be a non-empty object")
    baseline_missing = sorted(REQUIRED_CONFIGURATION_FIELDS - set(required))
    if baseline_missing:
        raise ValueError(f"required_configuration missing server baseline fields: {', '.join(baseline_missing)}")
    if "as_of_date" not in requirement:
        raise ValueError("requirement.as_of_date is required for deterministic quote freshness")
    as_of = require_iso_date(requirement["as_of_date"], "as_of_date")
    offered = quote.get("configuration", {})
    mismatches = []
    missing = []
    for field, expected in required.items():
        actual = offered.get(field)
        if is_unresolved(actual):
            missing.append(field)
        elif not _equivalent(actual, expected):
            mismatches.append({"field": field, "required": expected, "offered": actual})

    commercial_missing = []
    costs: dict[str, Decimal] = {}
    for field in COST_FIELDS:
        if field not in quote or is_unresolved(quote.get(field)):
            commercial_missing.append(field)
        else:
            costs[field] = require_decimal(quote[field], field, minimum=Decimal("0"))
    for field in ("quote_id", "supplier", "sales_channel", "currency", "tax_included", "orderability_confirmed", "source_date", "quote_valid_until"):
        if field not in quote or is_unresolved(quote.get(field)):
            commercial_missing.append(field)

    expired = False
    if quote.get("currency"):
        require_currency(quote["currency"])
    if quote.get("source_date"):
        source_date = require_iso_date(quote["source_date"], "source_date")
        max_age_days = require_float(requirement.get("max_quote_age_days", 90), "max_quote_age_days", minimum=0)
        stale = (as_of - source_date).days > max_age_days or source_date > as_of
    else:
        stale = False
    if quote.get("quote_valid_until"):
        valid_until = require_iso_date(quote["quote_valid_until"], "quote_valid_until")
        expired = valid_until < as_of

    orderable = False
    if "orderability_confirmed" in quote:
        orderable = require_bool(quote["orderability_confirmed"], "orderability_confirmed")
    if "tax_included" in quote:
        require_bool(quote["tax_included"], "tax_included")

    technical_pass = not missing and not mismatches
    commercial_pass = not commercial_missing and orderable and not expired and not stale
    total = sum(costs.values(), Decimal("0")) if not commercial_missing else None
    reasons = []
    if missing:
        reasons.append("configuration-fields-missing")
    if mismatches:
        reasons.append("configuration-mismatch")
    if commercial_missing:
        reasons.append("commercial-fields-missing")
    if not orderable:
        reasons.append("orderability-not-confirmed")
    if expired:
        reasons.append("quote-expired")
    if stale:
        reasons.append("quote-stale-or-future-dated")

    return {
        "quote_id": quote.get("quote_id"),
        "supplier": quote.get("supplier"),
        "sales_channel": quote.get("sales_channel"),
        "technical_fit_status": "PASS" if technical_pass else "FAIL",
        "commercial_status": "PASS" if commercial_pass else "FAIL",
        "eligible_for_pricing": technical_pass and commercial_pass,
        "missing_configuration_fields": missing,
        "configuration_mismatches": mismatches,
        "missing_commercial_fields": commercial_missing,
        "normalized_comparable_cost": float(total) if total is not None else None,
        "currency": quote.get("currency"),
        "reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate server quotes against a frozen RFQ baseline")
    parser.add_argument("input", type=Path, help="JSON containing requirement and quotes")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    result = {"results": [validate_quote(data["requirement"], q) for q in data["quotes"]]}
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

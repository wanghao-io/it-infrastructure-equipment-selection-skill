#!/usr/bin/env python3
"""Validate server quotations against a frozen RFQ baseline."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from contracts import (
    is_unresolved,
    require_bool,
    require_currency,
    require_decimal,
    require_float,
    require_iso_date,
    strict_json_dumps,
    strict_json_loads,
)
from validate_json_schemas import validate_file

COST_FIELDS = (
    "hardware_price", "mandatory_accessories", "required_licenses",
    "warranty_support", "required_implementation", "tax_amount", "shipping",
)
REQUIRED_CONFIGURATION_FIELDS = {
    "cpu_cores", "memory_gb", "usable_storage_tb", "raid_cache_with_plp",
    "network_ports_10gbe", "redundant_power", "warranty_years",
}
V2_REQUIRED_CONFIGURATION_FIELDS = {
    "cpu_model", "cpu_socket_count", "cpu_cores", "memory_gb", "dimm_count",
    "storage_media", "drive_count", "drive_capacity_tb", "raid_level", "usable_storage_tb",
    "raid_cache_with_plp", "nic_model", "network_ports_10gbe", "optics_included",
    "redundant_power", "psu_count", "rails_included", "warranty_years", "service_level",
}
IDENTITY_FIELDS = ("quote_id", "supplier", "sales_channel")


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
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _equivalent(actual[key], value) for key, value in expected.items()
        )
    return str(actual).strip().casefold() == str(expected).strip().casefold()


def _valid_identity_text(value: Any) -> bool:
    return isinstance(value, str) and not is_unresolved(value) and bool(value.strip())


def validate_quote(
    requirement: dict[str, Any], quote: dict[str, Any], *, contract_version: int = 1
) -> dict[str, Any]:
    required = requirement.get("required_configuration", {})
    if not isinstance(required, dict) or not required:
        raise ValueError("required_configuration must be a non-empty object")
    required_fields = REQUIRED_CONFIGURATION_FIELDS if contract_version == 1 else V2_REQUIRED_CONFIGURATION_FIELDS
    baseline_missing = sorted(required_fields - set(required))
    if baseline_missing:
        raise ValueError(f"required_configuration missing server baseline fields: {', '.join(baseline_missing)}")
    if "as_of_date" not in requirement:
        raise ValueError("requirement.as_of_date is required for deterministic quote freshness")
    as_of = require_iso_date(requirement["as_of_date"], "as_of_date")
    offered = quote.get("configuration", {})
    if not isinstance(offered, dict):
        offered = {}
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
    for field in ("currency", "tax_included", "orderability_confirmed", "source_date", "quote_valid_until"):
        if field not in quote or is_unresolved(quote.get(field)):
            commercial_missing.append(field)
    for field in IDENTITY_FIELDS:
        if not _valid_identity_text(quote.get(field)):
            commercial_missing.append(field)
    if contract_version >= 2:
        for field in ("commercial_scope_id", "tax_basis", "delivery_basis"):
            if not _valid_identity_text(quote.get(field)):
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
    # A minimum-capacity PASS is not an exact purchasing configuration. Keep
    # upgraded alternatives visible, but never merge their prices into this RFQ.
    exact_match = technical_pass and all(
        field in offered and _exact(offered[field], expected)
        for field, expected in required.items()
    ) and set(offered) == set(required)
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
    if contract_version >= 2 and technical_pass and not exact_match:
        reasons.append("technically-eligible-alternative-not-exact")

    return {
        "quote_id": quote.get("quote_id"),
        "supplier": quote.get("supplier"),
        "sales_channel": quote.get("sales_channel"),
        "source_date": quote.get("source_date"),
        "quote_valid_until": quote.get("quote_valid_until"),
        "technical_fit_status": "FAIL" if mismatches else "CONDITIONAL" if missing else "PASS",
        "commercial_status": "PASS" if commercial_pass else "CONDITIONAL" if commercial_missing else "FAIL",
        "eligible_for_pricing": technical_pass and commercial_pass and (contract_version == 1 or exact_match),
        "exact_configuration_match": exact_match if contract_version >= 2 else False,
        "configuration_match_level": ("exact-procurement-object" if exact_match else "technical-alternative") if contract_version >= 2 else "coarse-minimum",
        "match_scope": "declared-rfq-fields-only; not proof of lifecycle or deployment compatibility",
        "contract_version": contract_version,
        "missing_configuration_fields": missing,
        "configuration_mismatches": mismatches,
        "missing_commercial_fields": commercial_missing,
        "normalized_comparable_cost": float(total) if total is not None else None,
        "currency": quote.get("currency"),
        "reasons": reasons,
    }


def _exact(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and set(actual) == set(expected) and all(
            _exact(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            _exact(a, b) for a, b in zip(actual, expected)
        )
    if isinstance(expected, bool):
        return type(actual) is bool and actual == expected
    if isinstance(expected, (int, float)):
        return not isinstance(actual, bool) and Decimal(str(actual)) == Decimal(str(expected))
    return str(actual).strip().casefold() == str(expected).strip().casefold()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate server quotes against a frozen RFQ baseline")
    parser.add_argument("input", type=Path, help="JSON containing requirement and quotes")
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
    result = {
        "contract_version": version,
        "results": [validate_quote(data["requirement"], q, contract_version=version) for q in data["quotes"]],
    }
    print(strict_json_dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

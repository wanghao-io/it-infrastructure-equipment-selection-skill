#!/usr/bin/env python3
"""Shared validation helpers for risk-sensitive workflow inputs."""

from __future__ import annotations

import math
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

UNRESOLVED_MARKERS = {
    "",
    "tbd",
    "unknown",
    "needs confirmation",
    "to be confirmed",
    "待确认",
    "未确认",
    "待定",
    "未知",
}


def is_unresolved(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in UNRESOLVED_MARKERS
    return False


def require_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} must be a JSON boolean")
    return value


def optional_bool(value: Any, field: str, *, default: bool = False) -> bool:
    if value is None:
        return default
    return require_bool(value, field)


def require_decimal(value: Any, field: str, *, minimum: Decimal = Decimal("0")) -> Decimal:
    if isinstance(value, bool) or is_unresolved(value):
        raise ValueError(f"{field} must be a finite number")
    text = str(value).replace(",", "").replace("¥", "").replace("￥", "").strip()
    try:
        result = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not result.is_finite() or result < minimum:
        raise ValueError(f"{field} must be finite and >= {minimum}")
    return result


def optional_decimal(value: Any, field: str, *, default: Decimal = Decimal("0")) -> Decimal:
    if value is None or value == "":
        return default
    return require_decimal(value, field)


def require_float(
    value: Any,
    field: str,
    *,
    minimum: float = 0.0,
    maximum: float | None = None,
) -> float:
    result = float(require_decimal(value, field, minimum=Decimal(str(minimum))))
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    if maximum is not None and result > maximum:
        raise ValueError(f"{field} must be <= {maximum}")
    return result


def require_int(value: Any, field: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    result = require_float(value, field, minimum=float(minimum), maximum=float(maximum) if maximum is not None else None)
    if not result.is_integer():
        raise ValueError(f"{field} must be an integer")
    return int(result)


def require_enum(value: Any, field: str, allowed: Iterable[str]) -> str:
    allowed_set = {str(item) for item in allowed}
    result = str(value).strip()
    if result not in allowed_set:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(allowed_set))}")
    return result


def require_currency(value: Any, field: str = "currency") -> str:
    result = str(value or "").strip().upper()
    if len(result) != 3 or not result.isalpha():
        raise ValueError(f"{field} must be a three-letter currency code")
    return result


def require_iso_date(value: Any, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD)") from exc


def base_result(status: str = "READY") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": status,
        "errors": [],
        "warnings": [],
        "assumptions": [],
        "provenance": [],
    }


def reject_non_finite_json_constant(value: str) -> None:
    """Reject Python's non-standard NaN/Infinity JSON extensions."""
    raise ValueError(f"non-standard JSON numeric constant is not allowed: {value}")


def strict_json_loads(text: str) -> Any:
    return json.loads(text, parse_constant=reject_non_finite_json_constant)


def strict_json_dumps(value: Any, **kwargs: Any) -> str:
    """Serialize machine output as standards-compliant JSON only."""
    return json.dumps(value, allow_nan=False, **kwargs)

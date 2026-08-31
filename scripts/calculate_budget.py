#!/usr/bin/env python3
"""Calculate BOM subtotal and contingency from a CSV budget file."""

from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from contracts import require_float, require_decimal, strict_json_dumps


def number(value) -> Decimal:
    if value is None:
        raise ValueError("unresolved amount")
    text = str(value).replace(",", "").replace("¥", "").replace("￥", "").strip()
    if not text or text.lower() in {"tbd", "unknown", "needs confirmation", "待确认", "待定"}:
        raise ValueError("unresolved amount")
    return require_decimal(text, "amount", minimum=Decimal(0))


def calculate(rows: list[dict], contingency_percent: float = 10.0) -> dict:
    contingency_percent = require_float(
        contingency_percent, "contingency_percent", minimum=0, maximum=100
    )
    subtotal = Decimal(0)
    incomplete_rows = []
    conflicts = []
    quantum = Decimal("0.01")
    def money(value):
        return float(value.quantize(quantum, rounding=ROUND_HALF_UP))
    for index, row in enumerate(rows, start=1):
        if row.get("类别") == "汇总" or row.get("category") == "summary":
            continue
        explicit_total = row.get("估算合计（元）", row.get("total", row.get("Total")))
        qty_value = row.get("数量", row.get("qty", row.get("Quantity")))
        price_value = row.get("估算单价（元）", row.get("unit_price", row.get("Unit Price")))
        try:
            total = number(explicit_total) if explicit_total not in (None, "") else None
            basis = row.get("pricing_basis", "quantity-unit")
            if basis not in {"quantity-unit", "lump-sum"}:
                raise ValueError("unsupported pricing_basis")
            if basis == "lump-sum":
                if total is None or not str(row.get("pricing_note", "")).strip():
                    raise ValueError("lump-sum needs explicit amount and pricing_note")
                subtotal += total
                continue
            # Legacy amount-only lines remain valid; when quantity/unit are
            # supplied they must agree, including on drafts.
            if qty_value is not None or price_value is not None or total is None:
                expected = number(qty_value) * number(price_value)
                if total is not None and money(total) != money(expected):
                    conflicts.append({"row": index, "reason": "quantity-unit-total-mismatch",
                                      "expected": money(expected), "provided": money(total),
                                      "difference": money(total - expected)})
                    incomplete_rows.append(index)
                    continue
                total = expected if total is None else total
            subtotal += total
        except ValueError:
            incomplete_rows.append(index)

    contingency = subtotal * Decimal(str(contingency_percent)) / 100
    return {
        "status": "complete" if not incomplete_rows else "incomplete-needs-confirmation",
        "incomplete_rows": incomplete_rows,
        "conflicts": conflicts,
        "known_cost_floor": money(subtotal),
        "subtotal": money(subtotal) if not incomplete_rows else None,
        "contingency_percent": contingency_percent,
        "contingency": money(contingency),
        "total_with_contingency": money(subtotal + contingency) if not incomplete_rows else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate budget subtotal and contingency")
    parser.add_argument("input", type=Path)
    parser.add_argument("--contingency-percent", type=float, default=10.0)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(strict_json_dumps(calculate(rows, args.contingency_percent), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

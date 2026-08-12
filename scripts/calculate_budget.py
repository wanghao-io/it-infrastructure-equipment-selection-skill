#!/usr/bin/env python3
"""Calculate BOM subtotal and contingency from a CSV budget file."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def number(value) -> float:
    if value is None:
        raise ValueError("unresolved amount")
    text = str(value).replace(",", "").replace("¥", "").replace("￥", "").strip()
    if not text or text.lower() in {"tbd", "unknown", "needs confirmation", "待确认", "待定"}:
        raise ValueError("unresolved amount")
    value = float(text)
    if value < 0:
        raise ValueError("amount must be non-negative")
    return value


def calculate(rows: list[dict], contingency_percent: float = 10.0) -> dict:
    if contingency_percent < 0:
        raise ValueError("contingency_percent must be non-negative")
    subtotal = 0.0
    incomplete_rows = []
    for index, row in enumerate(rows, start=1):
        if row.get("类别") == "汇总" or row.get("category") == "summary":
            continue
        explicit_total = row.get("估算合计（元）", row.get("total", row.get("Total")))
        if explicit_total not in (None, ""):
            try:
                subtotal += number(explicit_total)
            except ValueError:
                incomplete_rows.append(index)
        else:
            try:
                qty = number(row.get("数量", row.get("qty", row.get("Quantity"))))
                unit_price = number(row.get("估算单价（元）", row.get("unit_price", row.get("Unit Price"))))
                subtotal += qty * unit_price
            except ValueError:
                incomplete_rows.append(index)

    contingency = subtotal * contingency_percent / 100.0
    return {
        "status": "complete" if not incomplete_rows else "incomplete-needs-confirmation",
        "incomplete_rows": incomplete_rows,
        "known_cost_floor": round(subtotal, 2),
        "subtotal": round(subtotal, 2) if not incomplete_rows else None,
        "contingency_percent": contingency_percent,
        "contingency": round(contingency, 2),
        "total_with_contingency": round(subtotal + contingency, 2) if not incomplete_rows else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate budget subtotal and contingency")
    parser.add_argument("input", type=Path)
    parser.add_argument("--contingency-percent", type=float, default=10.0)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(json.dumps(calculate(rows, args.contingency_percent), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

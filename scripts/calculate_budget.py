#!/usr/bin/env python3
"""Calculate BOM subtotal and contingency from a CSV budget file."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def number(value) -> float:
    if value is None:
        return 0.0
    text = str(value).replace(",", "").replace("¥", "").replace("￥", "").strip()
    return float(text) if text else 0.0


def calculate(rows: list[dict], contingency_percent: float = 10.0) -> dict:
    subtotal = 0.0
    for row in rows:
        if row.get("类别") == "汇总" or row.get("category") == "summary":
            continue
        explicit_total = row.get("估算合计（元）", row.get("total"))
        if explicit_total not in (None, ""):
            subtotal += number(explicit_total)
        else:
            qty = number(row.get("数量", row.get("qty", 0)))
            unit_price = number(row.get("估算单价（元）", row.get("unit_price", 0)))
            subtotal += qty * unit_price

    contingency = subtotal * contingency_percent / 100.0
    return {
        "subtotal": round(subtotal, 2),
        "contingency_percent": contingency_percent,
        "contingency": round(contingency, 2),
        "total_with_contingency": round(subtotal + contingency, 2),
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

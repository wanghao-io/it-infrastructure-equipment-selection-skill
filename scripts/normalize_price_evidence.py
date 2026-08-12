#!/usr/bin/env python3
"""Normalize price evidence to comparable project cost scope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def normalized_cost(item: Dict[str, Any]) -> float:
    base = float(item.get("hardware_price", item.get("price", 0)) or 0)
    accessories = float(item.get("mandatory_accessories", 0) or 0)
    licenses = float(item.get("required_licenses", 0) or 0)
    support = float(item.get("warranty_support", 0) or 0)
    implementation = float(item.get("required_implementation", 0) or 0)
    tax = float(item.get("tax_amount", 0) or 0)
    shipping = float(item.get("shipping", 0) or 0)
    return base + accessories + licenses + support + implementation + tax + shipping


def normalize(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    output = []
    for item in items:
        row = dict(item)
        row["normalized_comparable_cost"] = round(normalized_cost(item), 2)
        missing = []
        for key in ("configuration", "source_type", "source_date"):
            if not item.get(key):
                missing.append(key)
        row["comparison_ready"] = bool(item.get("comparable", False)) and not missing
        row["missing_fields"] = missing
        output.append(row)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize procurement price evidence")
    parser.add_argument("input", type=Path, help="JSON file containing an array or {'items': [...]} object")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    result = normalize(items)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

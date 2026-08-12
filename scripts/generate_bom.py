#!/usr/bin/env python3
"""Generate an Excel-friendly BOM/budget CSV.

Uses UTF-8 with BOM by default so Chinese fields open correctly in common
Windows/Excel workflows.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from calculate_budget import calculate

DEFAULT_CN_FIELDS = [
    "序号",
    "类别",
    "设备/服务",
    "配置或范围",
    "数量",
    "单位",
    "估算单价（元）",
    "估算合计（元）",
    "价格口径",
    "证据等级",
    "参考来源",
    "备注",
]


def generate(items: Sequence[Mapping], filename: str = "bom.csv", fieldnames: Iterable[str] | None = None) -> None:
    if not items:
        raise ValueError("items must not be empty")
    fields = list(fieldnames or items[0].keys())
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)


def add_budget_summary(items: list[dict], contingency_percent: float = 0.0) -> dict:
    return calculate(items, contingency_percent)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BOM CSV from JSON")
    parser.add_argument("input", type=Path, help="JSON array or {'items': [...]} file")
    parser.add_argument("output", type=Path)
    parser.add_argument("--contingency-percent", type=float, default=0.0)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("input must contain a list of items")

    fieldnames = DEFAULT_CN_FIELDS if items and set(DEFAULT_CN_FIELDS).intersection(items[0].keys()) else None
    generate(items, str(args.output), fieldnames=fieldnames)
    print(json.dumps(add_budget_summary(items, args.contingency_percent), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate an Excel-friendly BOM/budget CSV.

Uses UTF-8 with BOM by default so Chinese fields open correctly in common
Windows/Excel workflows.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from calculate_budget import calculate
from contracts import strict_json_loads

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


def generate(
    items: Sequence[Mapping],
    filename: str = "bom.csv",
    fieldnames: Iterable[str] | None = None,
    *,
    overwrite: bool = False,
) -> None:
    if not items:
        raise ValueError("items must not be empty")
    output = Path(filename)
    if output.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {output}")
    fields = list(fieldnames or [])
    for item in items:
        for key in item:
            if key not in fields:
                fields.append(key)
    if not fields:
        raise ValueError("BOM fields must not be empty")
    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8-sig", dir=output.parent, delete=False
    )
    temporary = Path(handle.name)
    try:
        f = handle
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)
        f.flush()
        os.fsync(f.fileno())
        f.close()
        os.replace(temporary, output)
    except Exception:
        handle.close()
        temporary.unlink(missing_ok=True)
        raise


def add_budget_summary(items: list[dict], contingency_percent: float = 0.0) -> dict:
    return calculate(items, contingency_percent)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BOM CSV from JSON")
    parser.add_argument("input", type=Path, help="JSON array or {'items': [...]} file")
    parser.add_argument("output", type=Path)
    parser.add_argument("--contingency-percent", type=float, default=0.0)
    parser.add_argument("--force", action="store_true", help="Replace an existing output after full prevalidation")
    parser.add_argument("--stage", choices=("draft", "rfq-ready", "budget-complete"), default="budget-complete",
                        help="Draft/RFQ may retain TBD prices; no stage certifies procurement eligibility")
    args = parser.parse_args()

    data = strict_json_loads(args.input.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("input must contain a list of items")

    summary = add_budget_summary(items, args.contingency_percent)
    if summary["conflicts"]:
        raise ValueError(f"BOM row contradictions: {summary['conflicts']}; no output file was written")
    if args.stage == "budget-complete" and summary["status"] != "complete":
        raise ValueError("BOM budget contains unresolved rows; no output file was written")
    summary["delivery_stage"] = args.stage
    summary["procurement_ready"] = False
    summary["scope_note"] = "Amount calculation/rendering only; technical and commercial evidence require separate review."
    if args.stage in {"draft", "rfq-ready"}:
        items = [dict(item, delivery_stage=args.stage, budget_status=summary["status"]) for item in items]
    fieldnames = DEFAULT_CN_FIELDS if items and any(set(DEFAULT_CN_FIELDS).intersection(item.keys()) for item in items) else None
    generate(items, str(args.output), fieldnames=fieldnames, overwrite=args.force)
    print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate HCI failure-domain capacity after the requested node loss."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from contracts import require_bool, require_float

DIMENSIONS = ("cpu_cores", "memory_gb", "usable_storage_tb", "storage_iops", "network_gbps")


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    nodes = int(require_float(data.get("nodes"), "nodes", minimum=1))
    failed_nodes = int(require_float(data.get("failed_nodes", 1), "failed_nodes", minimum=1))
    if nodes < 3 or failed_nodes >= nodes:
        raise ValueError("HCI N+1 requires at least 3 nodes and fewer failed_nodes than nodes")
    per_node = data.get("per_node_capacity", {})
    workload = data.get("workload_demand", {})
    reserve = data.get("reserve_ratio", {})
    checks = {}
    remaining = nodes - failed_nodes
    for dimension in DIMENSIONS:
        capacity = require_float(per_node.get(dimension), f"per_node_capacity.{dimension}", minimum=0)
        demand = require_float(workload.get(dimension), f"workload_demand.{dimension}", minimum=0)
        ratio = require_float(reserve.get(dimension, 0), f"reserve_ratio.{dimension}", minimum=0, maximum=0.95)
        failover_capacity = remaining * capacity * (1 - ratio)
        checks[dimension] = {
            "demand": round(demand, 4),
            "failover_capacity_after_reserve": round(failover_capacity, 4),
            "headroom": round(failover_capacity - demand, 4),
            "pass": failover_capacity >= demand,
        }

    protection = require_bool(data.get("storage_protection_valid"), "storage_protection_valid")
    network = require_bool(data.get("network_redundancy_valid"), "network_redundancy_valid")
    failure_domains = require_bool(data.get("failure_domains_independent"), "failure_domains_independent")
    overall = all(row["pass"] for row in checks.values()) and protection and network and failure_domains
    return {
        "status": "PASS" if overall else "FAIL",
        "policy": f"N+{failed_nodes}",
        "nodes": nodes,
        "remaining_nodes": remaining,
        "dimension_checks": checks,
        "storage_protection_valid": protection,
        "network_redundancy_valid": network,
        "failure_domains_independent": failure_domains,
        "eligible_for_final_design": overall,
        "note": "Passing capacity math does not replace vendor support-matrix and failure-domain validation.",
    }


def check_n_plus_one(nodes: int, cpu_total: float, memory_total: float) -> bool:
    """Compatibility wrapper; use calculate() for procurement-grade validation."""
    if nodes < 3:
        return False
    remaining = nodes - 1
    return remaining * cpu_total / nodes >= cpu_total * 0.7 and remaining * memory_total / nodes >= memory_total * 0.7


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate HCI capacity after node failure")
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(calculate(data), ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

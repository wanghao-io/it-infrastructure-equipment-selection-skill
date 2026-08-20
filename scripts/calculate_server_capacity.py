#!/usr/bin/env python3
"""Workload-driven server capacity estimation helpers.

Supports both consolidated service workloads and legacy VM-count estimates. The
result is an engineering estimate, not a substitute for vendor/application
sizing guidance.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable

from contracts import require_float, require_int, strict_json_dumps


def calculate_virtualization(
    vm_count: int,
    avg_vcpu: float,
    avg_memory_gb: float,
    cpu_overcommit: float = 3.0,
    cpu_headroom: float = 0.25,
    memory_headroom: float = 0.30,
) -> Dict[str, Any]:
    vm_count = require_int(vm_count, "vm_count", minimum=0)
    avg_vcpu = require_float(avg_vcpu, "avg_vcpu", minimum=0)
    avg_memory_gb = require_float(avg_memory_gb, "avg_memory_gb", minimum=0)
    cpu_overcommit = require_float(cpu_overcommit, "cpu_overcommit", minimum=0.000001)
    cpu_headroom = require_float(cpu_headroom, "cpu_headroom", minimum=0)
    memory_headroom = require_float(memory_headroom, "memory_headroom", minimum=0)

    base_cores = vm_count * avg_vcpu / cpu_overcommit
    base_memory = vm_count * avg_memory_gb
    return {
        "mode": "virtualization",
        "estimated_physical_cpu_cores": max(1, math.ceil(base_cores * (1 + cpu_headroom))),
        "estimated_memory_gb": max(1, math.ceil(base_memory * (1 + memory_headroom))),
        "assumptions": {
            "cpu_overcommit": cpu_overcommit,
            "cpu_headroom": cpu_headroom,
            "memory_headroom": memory_headroom,
        },
    }


def calculate_services(
    services: Iterable[Dict[str, Any]],
    cpu_headroom: float = 0.25,
    memory_headroom: float = 0.25,
    os_cpu_cores: float = 1.0,
    os_memory_gb: float = 4.0,
    minimum_cpu_cores: int = 0,
    minimum_memory_gb: int = 0,
) -> Dict[str, Any]:
    cpu_headroom = require_float(cpu_headroom, "cpu_headroom", minimum=0)
    memory_headroom = require_float(memory_headroom, "memory_headroom", minimum=0)
    os_cpu_cores = require_float(os_cpu_cores, "os_cpu_cores", minimum=0)
    os_memory_gb = require_float(os_memory_gb, "os_memory_gb", minimum=0)
    minimum_cpu_cores = require_int(minimum_cpu_cores, "minimum_cpu_cores", minimum=0)
    minimum_memory_gb = require_int(minimum_memory_gb, "minimum_memory_gb", minimum=0)
    service_list = list(services)
    cpu = os_cpu_cores
    memory = os_memory_gb
    breakdown = []

    for service in service_list:
        name = str(service.get("name", "unnamed-service"))
        cores = require_float(service.get("cpu_cores", 0) or 0, f"{name}.cpu_cores", minimum=0)
        mem = require_float(service.get("memory_gb", 0) or 0, f"{name}.memory_gb", minimum=0)
        cpu += cores
        memory += mem
        breakdown.append({"name": name, "cpu_cores": cores, "memory_gb": mem})

    recommended_cpu = max(minimum_cpu_cores, math.ceil(cpu * (1 + cpu_headroom)))
    recommended_memory = max(minimum_memory_gb, math.ceil(memory * (1 + memory_headroom)))

    return {
        "mode": "consolidated-services",
        "service_breakdown": breakdown,
        "base_cpu_cores_including_os": round(cpu, 2),
        "base_memory_gb_including_os": round(memory, 2),
        "recommended_cpu_cores": recommended_cpu,
        "recommended_memory_gb": recommended_memory,
        "assumptions": {
            "cpu_headroom": cpu_headroom,
            "memory_headroom": memory_headroom,
            "os_cpu_cores": os_cpu_cores,
            "os_memory_gb": os_memory_gb,
        },
        "warning": "Validate SCADA/database/BI sizing and supported CPU/OS platform with the software vendors before procurement.",
    }


def calculate(vm_count: int, avg_vcpu: float, avg_memory_gb: float, cpu_overcommit: float = 3.0) -> Dict[str, Any]:
    """Backward-compatible wrapper for the original VM-count API."""
    return calculate_virtualization(vm_count, avg_vcpu, avg_memory_gb, cpu_overcommit)


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate server CPU and memory capacity")
    parser.add_argument("--services-json", type=Path, help="JSON file containing {'services': [...]} and optional sizing parameters")
    parser.add_argument("--vm-count", type=int)
    parser.add_argument("--avg-vcpu", type=float)
    parser.add_argument("--avg-memory-gb", type=float)
    parser.add_argument("--cpu-overcommit", type=float, default=3.0)
    args = parser.parse_args()

    if args.services_json:
        data = json.loads(args.services_json.read_text(encoding="utf-8"))
        result = calculate_services(
            data.get("services", []),
            cpu_headroom=float(data.get("cpu_headroom", 0.25)),
            memory_headroom=float(data.get("memory_headroom", 0.25)),
            os_cpu_cores=float(data.get("os_cpu_cores", 1.0)),
            os_memory_gb=float(data.get("os_memory_gb", 4.0)),
            minimum_cpu_cores=int(data.get("minimum_cpu_cores", 0)),
            minimum_memory_gb=int(data.get("minimum_memory_gb", 0)),
        )
    elif args.vm_count is not None and args.avg_vcpu is not None and args.avg_memory_gb is not None:
        result = calculate_virtualization(args.vm_count, args.avg_vcpu, args.avg_memory_gb, args.cpu_overcommit)
    else:
        parser.error("provide --services-json or all of --vm-count --avg-vcpu --avg-memory-gb")

    print(strict_json_dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

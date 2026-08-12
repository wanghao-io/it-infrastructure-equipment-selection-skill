#!/usr/bin/env python3
"""UPS power and short-runtime sizing helper.

Runtime output is an engineering target only. Actual battery runtime must be
validated against the selected UPS manufacturer's runtime curve.
"""

from __future__ import annotations

import argparse
import json
import math


def calculate(
    load_w: float,
    power_factor: float = 0.90,
    capacity_margin: float = 1.30,
    runtime_minutes: float = 10.0,
    inverter_efficiency: float = 0.85,
) -> dict:
    if load_w <= 0:
        raise ValueError("load_w must be > 0")
    if not 0 < power_factor <= 1:
        raise ValueError("power_factor must be in (0, 1]")
    if capacity_margin < 1:
        raise ValueError("capacity_margin must be >= 1")
    if runtime_minutes < 0:
        raise ValueError("runtime_minutes must be >= 0")
    if not 0 < inverter_efficiency <= 1:
        raise ValueError("inverter_efficiency must be in (0, 1]")

    required_w = load_w * capacity_margin
    required_va = required_w / power_factor
    ideal_battery_wh = (load_w * runtime_minutes / 60.0) / inverter_efficiency

    # Round up to common coarse project sizing increments, not a product SKU.
    rounded_w = int(math.ceil(required_w / 100.0) * 100)
    rounded_va = int(math.ceil(required_va / 100.0) * 100)

    return {
        "protected_load_w": round(load_w, 1),
        "minimum_output_w_with_margin": round(required_w, 1),
        "minimum_va_with_margin": round(required_va, 1),
        "coarse_project_target_w": rounded_w,
        "coarse_project_target_va": rounded_va,
        "target_runtime_minutes": runtime_minutes,
        "idealized_minimum_battery_energy_wh": round(ideal_battery_wh, 1),
        "assumptions": {
            "power_factor": power_factor,
            "capacity_margin": capacity_margin,
            "inverter_efficiency": inverter_efficiency,
        },
        "required_features": [
            "waveform compatible with protected IT load",
            "communication interface for graceful shutdown when required",
            "vendor runtime curve meeting target runtime at actual load",
        ],
        "warning": "Do not infer actual runtime from Wh alone; validate the selected UPS runtime curve and battery condition at the real load.",
    }


def ups_rating(load_kw: float, margin: float = 1.3) -> float:
    """Backward-compatible W/kW margin helper."""
    if load_kw <= 0 or margin < 1:
        raise ValueError("load_kw must be > 0 and margin >= 1")
    return load_kw * margin


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate UPS W/VA target and short-runtime energy requirement")
    parser.add_argument("load_w", type=float)
    parser.add_argument("--power-factor", type=float, default=0.90)
    parser.add_argument("--margin", type=float, default=1.30)
    parser.add_argument("--runtime-minutes", type=float, default=10.0)
    parser.add_argument("--efficiency", type=float, default=0.85)
    args = parser.parse_args()

    print(json.dumps(calculate(
        args.load_w,
        args.power_factor,
        args.margin,
        args.runtime_minutes,
        args.efficiency,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

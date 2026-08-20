#!/usr/bin/env python3
"""UPS sizing and candidate technical-fit helper.

Pricing must follow the validated technical requirement. A cheaper UPS candidate
is not eligible for budget comparison merely because its nominal VA looks close.
Actual battery runtime must still be validated against the selected UPS
manufacturer's runtime curve.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any

from contracts import require_bool, require_float, strict_json_dumps


def calculate(
    load_w: float,
    power_factor: float = 0.90,
    capacity_margin: float = 1.30,
    runtime_minutes: float = 10.0,
    inverter_efficiency: float = 0.85,
) -> dict:
    load_w = require_float(load_w, "load_w", minimum=0.000001)
    power_factor = require_float(power_factor, "power_factor", minimum=0.000001, maximum=1)
    capacity_margin = require_float(capacity_margin, "capacity_margin", minimum=1)
    runtime_minutes = require_float(runtime_minutes, "runtime_minutes", minimum=0)
    inverter_efficiency = require_float(inverter_efficiency, "inverter_efficiency", minimum=0.000001, maximum=1)

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


def assess_candidate(
    load_w: float,
    candidate_output_w: float,
    candidate_va: float,
    *,
    power_factor: float = 0.90,
    capacity_margin: float = 1.30,
    runtime_minutes: float = 10.0,
    inverter_efficiency: float = 0.85,
    runtime_curve_verified: bool = False,
    graceful_shutdown_required: bool = True,
    shutdown_interface_verified: bool = False,
) -> dict[str, Any]:
    """Determine whether a UPS candidate is technically eligible for pricing.

    The result deliberately separates nominal capacity from runtime and shutdown
    integration. A candidate that fails any mandatory requirement must not be
    used as a cheaper price anchor for the project BOM.
    """
    candidate_output_w = require_float(candidate_output_w, "candidate_output_w", minimum=0.000001)
    candidate_va = require_float(candidate_va, "candidate_va", minimum=0.000001)
    runtime_curve_verified = require_bool(runtime_curve_verified, "runtime_curve_verified")
    graceful_shutdown_required = require_bool(graceful_shutdown_required, "graceful_shutdown_required")
    shutdown_interface_verified = require_bool(shutdown_interface_verified, "shutdown_interface_verified")

    sizing = calculate(
        load_w,
        power_factor,
        capacity_margin,
        runtime_minutes,
        inverter_efficiency,
    )

    output_w_ok = candidate_output_w >= float(sizing["minimum_output_w_with_margin"])
    va_ok = candidate_va >= float(sizing["minimum_va_with_margin"])
    runtime_ok = runtime_minutes <= 0 or runtime_curve_verified
    shutdown_ok = (not graceful_shutdown_required) or shutdown_interface_verified

    reasons: list[str] = []
    if not output_w_ok:
        reasons.append("candidate-output-W-below-required-margin")
    if not va_ok:
        reasons.append("candidate-VA-below-required-margin")
    if not runtime_ok:
        reasons.append("runtime-curve-not-verified-at-protected-load")
    if not shutdown_ok:
        reasons.append("graceful-shutdown-interface-not-verified")

    eligible = output_w_ok and va_ok and runtime_ok and shutdown_ok
    return {
        "status": "eligible-for-pricing" if eligible else "not-eligible-for-pricing",
        "eligible_for_pricing": eligible,
        "candidate_output_w": round(candidate_output_w, 1),
        "candidate_va": round(candidate_va, 1),
        "capacity_checks": {
            "output_w_ok": output_w_ok,
            "va_ok": va_ok,
        },
        "runtime_curve_verified": runtime_curve_verified,
        "graceful_shutdown_required": graceful_shutdown_required,
        "shutdown_interface_verified": shutdown_interface_verified,
        "reasons": reasons,
        "sizing": sizing,
        "rule": "Validate technical fit before comparing price; a cheaper undersized or unverified UPS cannot redefine the project requirement.",
    }


def ups_rating(load_kw: float, margin: float = 1.3) -> float:
    """Backward-compatible W/kW margin helper."""
    load_kw = require_float(load_kw, "load_kw", minimum=0.000001)
    margin = require_float(margin, "margin", minimum=1)
    return load_kw * margin


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate UPS W/VA target and optionally validate a candidate before pricing")
    parser.add_argument("load_w", type=float)
    parser.add_argument("--power-factor", type=float, default=0.90)
    parser.add_argument("--margin", type=float, default=1.30)
    parser.add_argument("--runtime-minutes", type=float, default=10.0)
    parser.add_argument("--efficiency", type=float, default=0.85)
    parser.add_argument("--candidate-w", type=float, help="Candidate UPS real output rating in W")
    parser.add_argument("--candidate-va", type=float, help="Candidate UPS apparent-power rating in VA")
    parser.add_argument(
        "--runtime-curve-verified",
        action="store_true",
        help="Manufacturer runtime data confirms the target runtime at the protected load",
    )
    parser.add_argument(
        "--shutdown-interface-verified",
        action="store_true",
        help="Required graceful-shutdown interface/software compatibility is confirmed",
    )
    parser.add_argument(
        "--no-graceful-shutdown-required",
        action="store_true",
        help="The project does not require UPS-triggered graceful shutdown",
    )
    args = parser.parse_args()

    if (args.candidate_w is None) != (args.candidate_va is None):
        parser.error("--candidate-w and --candidate-va must be supplied together")

    if args.candidate_w is not None and args.candidate_va is not None:
        result: Any = assess_candidate(
            args.load_w,
            args.candidate_w,
            args.candidate_va,
            power_factor=args.power_factor,
            capacity_margin=args.margin,
            runtime_minutes=args.runtime_minutes,
            inverter_efficiency=args.efficiency,
            runtime_curve_verified=args.runtime_curve_verified,
            graceful_shutdown_required=not args.no_graceful_shutdown_required,
            shutdown_interface_verified=args.shutdown_interface_verified,
        )
    else:
        result = calculate(
            args.load_w,
            args.power_factor,
            args.margin,
            args.runtime_minutes,
            args.efficiency,
        )

    print(strict_json_dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

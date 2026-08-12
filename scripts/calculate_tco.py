#!/usr/bin/env python3
"""Calculate comparable 3/5-year infrastructure TCO from explicit assumptions.

The calculator intentionally separates acquisition cost from operating cost.
Power input must be average IT power, not PSU nameplate wattage. PUE is applied
once to electricity and must not be double-counted as a separate cooling charge.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HOURS_PER_YEAR = 8760.0


def num(obj: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = float(obj.get(key, default) or 0.0)
    if value < 0:
        raise ValueError(f"{key} must be non-negative")
    return value


def calculate_candidate(
    candidate: dict[str, Any],
    *,
    years: int,
    electricity_rate_per_kwh: float,
    pue: float,
    hours_per_year: float = HOURS_PER_YEAR,
) -> dict[str, Any]:
    if years <= 0:
        raise ValueError("years must be positive")
    if electricity_rate_per_kwh < 0:
        raise ValueError("electricity_rate_per_kwh must be non-negative")
    if pue < 1.0:
        raise ValueError("pue must be >= 1.0")

    purchase = num(candidate, "purchase_cost")
    implementation = num(candidate, "one_time_implementation")
    average_it_power_w = num(candidate, "average_it_power_w")
    annual_support = num(candidate, "annual_support")
    annual_license = num(candidate, "annual_license")
    annual_facility = num(candidate, "annual_facility")
    annual_other = num(candidate, "annual_other_opex")

    capex = purchase + implementation
    energy_kwh = (average_it_power_w / 1000.0) * pue * hours_per_year * years
    energy_cost = energy_kwh * electricity_rate_per_kwh
    recurring_opex = (annual_support + annual_license + annual_facility + annual_other) * years
    total_opex = energy_cost + recurring_opex
    total_tco = capex + total_opex

    return {
        "name": candidate.get("name", "Unnamed"),
        "years": years,
        "capex": round(capex, 2),
        "energy_kwh": round(energy_kwh, 2),
        "energy_cost": round(energy_cost, 2),
        "recurring_opex": round(recurring_opex, 2),
        "total_opex": round(total_opex, 2),
        "total_tco": round(total_tco, 2),
        "annualized_tco": round(total_tco / years, 2),
    }


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    if "electricity_rate_per_kwh" not in data:
        raise ValueError(
            "electricity_rate_per_kwh is required; use 0 explicitly only when electricity is intentionally excluded."
        )

    rate = float(data["electricity_rate_per_kwh"])
    pue = float(data.get("pue", 1.0))
    hours = float(data.get("hours_per_year", HOURS_PER_YEAR))
    if hours <= 0:
        raise ValueError("hours_per_year must be positive")

    horizons = [int(x) for x in data.get("years", [3, 5])]
    if not horizons:
        raise ValueError("years must contain at least one horizon")
    candidates = data.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidates must be a non-empty list")

    results = []
    for candidate in candidates:
        for years in horizons:
            results.append(
                calculate_candidate(
                    candidate,
                    years=years,
                    electricity_rate_per_kwh=rate,
                    pue=pue,
                    hours_per_year=hours,
                )
            )

    return {
        "assumptions": {
            "electricity_rate_per_kwh": rate,
            "pue": pue,
            "hours_per_year": hours,
            "power_basis": "average_it_power_w (not PSU nameplate)",
            "pue_rule": "PUE is applied once to electricity; do not separately add cooling already represented by PUE.",
        },
        "results": results,
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Infrastructure TCO",
        "",
        "| Candidate | Years | CAPEX | Energy | Recurring OPEX | Total OPEX | Total TCO | Annualized TCO |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["results"]:
        lines.append(
            f"| {row['name']} | {row['years']} | {row['capex']:.2f} | {row['energy_cost']:.2f} | "
            f"{row['recurring_opex']:.2f} | {row['total_opex']:.2f} | {row['total_tco']:.2f} | "
            f"{row['annualized_tco']:.2f} |"
        )
    lines.extend(
        [
            "",
            "> TCO is only as reliable as the supplied workload, power, PUE, support, license and facility assumptions. "
            "Use comparable commercial scope across candidates.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate comparable infrastructure TCO from JSON input.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    result = calculate(data)
    if args.format == "markdown":
        print(to_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

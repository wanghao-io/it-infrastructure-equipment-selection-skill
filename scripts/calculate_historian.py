#!/usr/bin/env python3
"""Transparent SCADA historian capacity estimator."""

from __future__ import annotations

import argparse
import json


def calculate(
    historical_points: int,
    sample_seconds: float,
    bytes_per_record: float = 32.0,
    compression_factor: float = 1.0,
    retention_days: int = 365,
    overhead_factor: float = 1.25,
    growth_factor: float = 1.20,
) -> dict:
    if historical_points < 0:
        raise ValueError("historical_points must be >= 0")
    if sample_seconds <= 0:
        raise ValueError("sample_seconds must be > 0")
    if bytes_per_record <= 0:
        raise ValueError("bytes_per_record must be > 0")
    if not 0 < compression_factor <= 1:
        raise ValueError("compression_factor must be in (0, 1]")
    if retention_days <= 0:
        raise ValueError("retention_days must be > 0")

    records_per_day = historical_points * 86400.0 / sample_seconds
    raw_gb_per_day = records_per_day * bytes_per_record / 1_000_000_000
    effective_gb_per_day = raw_gb_per_day * compression_factor
    retained_gb = effective_gb_per_day * retention_days
    recommended_gb = retained_gb * overhead_factor * growth_factor

    return {
        "historical_points": historical_points,
        "effective_sample_seconds": sample_seconds,
        "records_per_day": round(records_per_day),
        "raw_gb_per_day": round(raw_gb_per_day, 3),
        "effective_gb_per_day": round(effective_gb_per_day, 3),
        "retention_days": retention_days,
        "retained_tb_before_overhead": round(retained_gb / 1000, 3),
        "recommended_online_capacity_tb": round(recommended_gb / 1000, 3),
        "assumptions": {
            "bytes_per_record": bytes_per_record,
            "compression_factor": compression_factor,
            "overhead_factor": overhead_factor,
            "growth_factor": growth_factor,
        },
        "warning": "Compression factor must be vendor-validated or measured; do not treat this estimate as a historian guarantee.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate SCADA historian storage")
    parser.add_argument("points", type=int)
    parser.add_argument("sample_seconds", type=float)
    parser.add_argument("--bytes-per-record", type=float, default=32.0)
    parser.add_argument("--compression-factor", type=float, default=1.0)
    parser.add_argument("--retention-days", type=int, default=365)
    parser.add_argument("--overhead-factor", type=float, default=1.25)
    parser.add_argument("--growth-factor", type=float, default=1.20)
    args = parser.parse_args()

    result = calculate(
        args.points,
        args.sample_seconds,
        args.bytes_per_record,
        args.compression_factor,
        args.retention_days,
        args.overhead_factor,
        args.growth_factor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

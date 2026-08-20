#!/usr/bin/env python3
"""RAID and retention-aware storage capacity helpers."""

from __future__ import annotations

import argparse
import json

from contracts import require_float, require_int, strict_json_dumps


def raid_usable_capacity(drive_count: int, drive_tb: float, raid: str) -> float:
    drive_count = require_int(drive_count, "drive_count", minimum=1)
    drive_tb = require_float(drive_tb, "drive_tb", minimum=0.000001)

    level = raid.lower().replace("raid", "")
    if level == "0":
        usable_drives = drive_count
    elif level == "1":
        if drive_count < 2:
            raise ValueError("RAID1 requires at least 2 drives")
        usable_drives = 1
    elif level == "5":
        if drive_count < 3:
            raise ValueError("RAID5 requires at least 3 drives")
        usable_drives = drive_count - 1
    elif level == "6":
        if drive_count < 4:
            raise ValueError("RAID6 requires at least 4 drives")
        usable_drives = drive_count - 2
    elif level == "10":
        if drive_count < 4 or drive_count % 2:
            raise ValueError("RAID10 requires an even number of at least 4 drives")
        usable_drives = drive_count / 2
    else:
        raise ValueError("supported RAID levels: 0, 1, 5, 6, 10")

    return usable_drives * drive_tb


def required_capacity_tb(
    daily_growth_gb: float,
    retention_days: int,
    database_overhead: float = 1.20,
    growth_reserve: float = 1.20,
    free_space_reserve: float = 1.20,
) -> float:
    daily_growth_gb = require_float(daily_growth_gb, "daily_growth_gb", minimum=0)
    retention_days = require_int(retention_days, "retention_days", minimum=1)
    database_overhead = require_float(database_overhead, "database_overhead", minimum=1)
    growth_reserve = require_float(growth_reserve, "growth_reserve", minimum=1)
    free_space_reserve = require_float(free_space_reserve, "free_space_reserve", minimum=1)
    gb = daily_growth_gb * retention_days
    gb *= database_overhead * growth_reserve * free_space_reserve
    return gb / 1000


def usable_capacity(raw_tb: float, replica: float = 2) -> float:
    """Backward-compatible helper for replicated/distributed storage estimates."""
    raw_tb = require_float(raw_tb, "raw_tb", minimum=0)
    replica = require_float(replica, "replica", minimum=0.000001)
    return raw_tb / replica


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate RAID usable capacity and optional retention requirement")
    parser.add_argument("--drives", type=int, required=True)
    parser.add_argument("--drive-tb", type=float, required=True)
    parser.add_argument("--raid", required=True, choices=["0", "1", "5", "6", "10", "raid0", "raid1", "raid5", "raid6", "raid10"])
    parser.add_argument("--daily-growth-gb", type=float)
    parser.add_argument("--retention-days", type=int)
    args = parser.parse_args()

    usable = raid_usable_capacity(args.drives, args.drive_tb, args.raid)
    result = {
        "drive_count": args.drives,
        "drive_tb": args.drive_tb,
        "raid": args.raid,
        "raw_capacity_tb": round(args.drives * args.drive_tb, 3),
        "usable_capacity_tb": round(usable, 3),
    }

    if args.daily_growth_gb is not None or args.retention_days is not None:
        if args.daily_growth_gb is None or args.retention_days is None:
            parser.error("--daily-growth-gb and --retention-days must be supplied together")
        required = required_capacity_tb(args.daily_growth_gb, args.retention_days)
        result["recommended_required_capacity_tb"] = round(required, 3)
        result["capacity_headroom_tb"] = round(usable - required, 3)
        result["meets_estimated_requirement"] = usable >= required

    result["warning"] = "RAID protects against some drive failures; it is not an independent backup."
    result["assumptions"] = {
        "database_overhead": 1.20 if args.daily_growth_gb is not None else None,
        "growth_reserve": 1.20 if args.daily_growth_gb is not None else None,
        "free_space_reserve": 1.20 if args.daily_growth_gb is not None else None,
    }
    print(strict_json_dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""RAID and retention-aware storage capacity helpers."""

from __future__ import annotations

import argparse
import json


def raid_usable_capacity(drive_count: int, drive_tb: float, raid: str) -> float:
    if drive_count <= 0 or drive_tb <= 0:
        raise ValueError("drive_count and drive_tb must be > 0")

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
    if daily_growth_gb < 0 or retention_days <= 0:
        raise ValueError("daily_growth_gb must be >= 0 and retention_days > 0")
    gb = daily_growth_gb * retention_days
    gb *= database_overhead * growth_reserve * free_space_reserve
    return gb / 1000


def usable_capacity(raw_tb: float, replica: float = 2) -> float:
    """Backward-compatible helper for replicated/distributed storage estimates."""
    if raw_tb < 0 or replica <= 0:
        raise ValueError("raw_tb must be >= 0 and replica must be > 0")
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
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

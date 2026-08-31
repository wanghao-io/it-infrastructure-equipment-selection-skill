#!/usr/bin/env python3
"""Validate explicit project evidence/delivery/acceptance records without discovery."""
import argparse
from pathlib import Path
from contracts import strict_json_dumps
from project_records import FAMILIES, check_record, load_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=FAMILIES)
    parser.add_argument("input", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--check-files", action="store_true", help="Only verify explicitly listed source files")
    args = parser.parse_args()
    result = check_record(load_record(args.input), args.family,
                          project_root=args.project_root, check_files=args.check_files)
    print(strict_json_dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(f"error: {exc}") from None

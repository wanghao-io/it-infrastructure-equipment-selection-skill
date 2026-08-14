#!/usr/bin/env python3
"""Extract exactly one version section from CHANGELOG.md for a release body."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^v?(?P<version>\d+\.\d+\.\d+)$")
HEADING_RE = re.compile(r"^##[ \t]+v(?P<version>\d+\.\d+\.\d+)(?:[ \t]+.*)?$")
H2_RE = re.compile(r"^##(?:[ \t]+|$)")


class ReleaseNotesError(ValueError):
    """Raised when a changelog cannot yield one unambiguous release section."""


def normalize_version(value: str) -> str:
    match = VERSION_RE.fullmatch(value.strip())
    if match is None:
        raise ReleaseNotesError("version must be vX.Y.Z or X.Y.Z")
    return match.group("version")


def extract_release_notes(changelog: str, version: str) -> str:
    """Return the requested changelog section, stopping at the next version."""
    normalized = normalize_version(version)
    lines = changelog.splitlines()
    version_headings = [
        (index, match.group("version"))
        for index, line in enumerate(lines)
        if (match := HEADING_RE.fullmatch(line)) is not None
    ]
    matches = [
        index for index, found_version in version_headings if found_version == normalized
    ]
    if len(matches) != 1:
        raise ReleaseNotesError(
            f"expected exactly one changelog section for v{normalized}; found {len(matches)}"
        )

    start = matches[0]
    end = next(
        (index for index, line in enumerate(lines) if index > start and H2_RE.match(line)),
        len(lines),
    )
    section_lines = lines[start:end]
    if not any(line.strip() and not line.lstrip().startswith("#") for line in section_lines[1:]):
        raise ReleaseNotesError(f"changelog section for v{normalized} has no release content")
    return "\n".join(section_lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract one release section from CHANGELOG.md")
    parser.add_argument("version", help="Release version as vX.Y.Z or X.Y.Z")
    parser.add_argument("--changelog", type=Path, default=ROOT / "CHANGELOG.md")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    notes = extract_release_notes(args.changelog.read_text(encoding="utf-8"), args.version)
    if args.output is None:
        print(notes, end="")
    else:
        args.output.write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()

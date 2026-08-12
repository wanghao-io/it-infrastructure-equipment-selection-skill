#!/usr/bin/env python3
"""Install this Agent Skill into a supported host discovery directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable

SKILL_NAME = "it-infrastructure-equipment-selection"

TARGET_ALIASES = {
    "claude": "claude-code",
    "github-copilot": "copilot",
    "gemini-cli": "gemini",
}

SUPPORTED_TARGETS = ("codex", "claude-code", "copilot", "gemini", "generic")

RUNTIME_ENTRIES = (
    "SKILL.md",
    "references",
    "scripts",
    "assets",
    "examples",
    "agents",
    "LICENSE",
)


def normalize_target(target: str) -> str:
    normalized = TARGET_ALIASES.get(target, target)
    if normalized not in SUPPORTED_TARGETS:
        raise ValueError(f"Unsupported target: {target}")
    return normalized


def resolve_destination(
    target: str,
    scope: str,
    *,
    home: Path | None = None,
    project_dir: Path | None = None,
) -> Path:
    """Return the skill installation directory for a host/scope pair."""
    target = normalize_target(target)
    home = (home or Path.home()).expanduser().resolve()

    if scope == "user":
        if target == "claude-code":
            base = home / ".claude" / "skills"
        elif target == "copilot":
            # Use the interoperable Agent Skills path by default.
            base = home / ".agents" / "skills"
        elif target == "gemini":
            # Gemini CLI explicitly supports ~/.agents/skills as an alias.
            base = home / ".agents" / "skills"
        else:
            # Codex and generic Agent-Skills-compatible hosts use the portable path.
            base = home / ".agents" / "skills"
        return base / SKILL_NAME

    if scope != "project":
        raise ValueError(f"Unsupported scope: {scope}")

    if project_dir is None:
        raise ValueError("--project-dir is required for project scope")

    project_dir = project_dir.expanduser().resolve()
    if target == "claude-code":
        base = project_dir / ".claude" / "skills"
    elif target == "copilot":
        base = project_dir / ".github" / "skills"
    elif target in {"gemini", "codex", "generic"}:
        base = project_dir / ".agents" / "skills"
    else:  # pragma: no cover - normalize_target prevents this
        raise ValueError(f"Unsupported target: {target}")
    return base / SKILL_NAME


def _remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def copy_runtime(source: Path, destination: Path, entries: Iterable[str] = RUNTIME_ENTRIES) -> None:
    """Copy only runtime-relevant skill files into destination."""
    destination.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        src = source / entry
        if not src.exists():
            continue
        dst = destination / entry
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def install_skill(
    source: Path,
    destination: Path,
    *,
    mode: str = "copy",
    force: bool = False,
    dry_run: bool = False,
) -> Path:
    """Install the skill and return the resolved destination."""
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve(strict=False)

    skill_file = source / "SKILL.md"
    if not skill_file.is_file():
        raise FileNotFoundError(f"SKILL.md not found in source: {source}")

    if mode not in {"copy", "symlink"}:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "copy" and _is_relative_to(destination, source):
        raise ValueError(
            "Copy destination is inside the source repository. "
            "Use another --project-dir or --mode symlink."
        )

    if destination.exists() or destination.is_symlink():
        if not force:
            raise FileExistsError(
                f"Destination already exists: {destination}. Use --force to replace it."
            )
        if not dry_run:
            _remove_existing(destination)

    if dry_run:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        destination.symlink_to(source, target_is_directory=True)
    else:
        copy_runtime(source, destination)

    return destination


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install IT Infrastructure Equipment Selection as a portable Agent Skill"
    )
    parser.add_argument(
        "--target",
        required=True,
        choices=sorted(set(SUPPORTED_TARGETS) | set(TARGET_ALIASES)),
        help="Agent host: codex, claude-code, copilot, gemini or generic",
    )
    parser.add_argument(
        "--scope",
        choices=("user", "project"),
        default="user",
        help="Install for the current user or into a project/workspace",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Project/workspace root; required with --scope project",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "symlink"),
        default="copy",
        help="Copy portable runtime files or symlink the repository",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing installed copy/symlink",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the destination without changing files",
    )
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1]
    destination = resolve_destination(
        args.target,
        args.scope,
        project_dir=args.project_dir,
    )
    installed = install_skill(
        source,
        destination,
        mode=args.mode,
        force=args.force,
        dry_run=args.dry_run,
    )

    action = "Would install" if args.dry_run else "Installed"
    print(f"{action} {SKILL_NAME} for {normalize_target(args.target)} at: {installed}")
    if not args.dry_run:
        print("Verify discovery in the target host before relying on the skill.")


if __name__ == "__main__":
    main()

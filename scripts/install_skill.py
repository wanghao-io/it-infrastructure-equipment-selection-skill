#!/usr/bin/env python3
"""Install or update this Agent Skill in a supported host discovery directory."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
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
    "VERSION",
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
            base = home / ".agents" / "skills"
        elif target == "gemini":
            base = home / ".agents" / "skills"
        else:
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
    else:  # pragma: no cover
        raise ValueError(f"Unsupported target: {target}")
    return base / SKILL_NAME


def _absolute_without_resolving_symlinks(path: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    return Path(os.path.abspath(expanded))


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


def is_git_checkout(path: Path) -> bool:
    """Return True for a normal Git checkout or worktree."""
    git_marker = path / ".git"
    return git_marker.is_dir() or git_marker.is_file()


def git_worktree_dirty(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def update_git_checkout(path: Path, *, dry_run: bool = False) -> Path:
    """Safely fast-forward an existing Git-installed skill."""
    if not is_git_checkout(path):
        raise ValueError(f"Not a Git checkout: {path}")
    skill_file = path / "SKILL.md"
    if not skill_file.is_file() or f"name: {SKILL_NAME}" not in skill_file.read_text(encoding="utf-8"):
        raise RuntimeError(f"Git checkout is not {SKILL_NAME}: {path}")
    if git_worktree_dirty(path):
        raise RuntimeError(
            f"Git installation has local changes: {path}. "
            "Commit/stash them before updating; automatic overwrite is disabled."
        )
    if not dry_run:
        subprocess.run(
            ["git", "-C", str(path), "pull", "--ff-only"],
            check=True,
        )
    return path


def copy_runtime(source: Path, destination: Path, entries: Iterable[str] = RUNTIME_ENTRIES) -> None:
    """Synchronize managed runtime entries while preserving unrelated local files."""
    destination.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        src = source / entry
        if not src.exists():
            continue
        dst = destination / entry
        if dst.exists() or dst.is_symlink():
            _remove_existing(dst)
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
    update: bool = False,
    dry_run: bool = False,
) -> Path:
    """Install or update the skill and return the destination path."""
    source = source.expanduser().resolve()
    destination = _absolute_without_resolving_symlinks(destination)

    skill_file = source / "SKILL.md"
    if not skill_file.is_file():
        raise FileNotFoundError(f"SKILL.md not found in source: {source}")

    if mode not in {"copy", "symlink"}:
        raise ValueError(f"Unsupported mode: {mode}")

    # A copied installation cannot safely update itself: managed entries such
    # as SKILL.md and scripts/ are both the source and destination. Refuse
    # before any removal so a failed update is always non-destructive.
    if mode == "copy" and source == destination.resolve(strict=False):
        if is_git_checkout(source) and update:
            return update_git_checkout(source, dry_run=dry_run)
        raise ValueError(
            "Copy source and destination are the same directory. "
            "Run updates from an independent clone or release package."
        )

    if update and (destination.exists() or destination.is_symlink()):
        if destination.is_symlink():
            target = destination.resolve()
            if is_git_checkout(target):
                update_git_checkout(target, dry_run=dry_run)
                return destination
            if target == source:
                return destination
            raise RuntimeError(
                f"Symlink target is not a Git checkout: {target}. "
                "Update the source directory manually."
            )

        if is_git_checkout(destination):
            update_git_checkout(destination, dry_run=dry_run)
            return destination

        if dry_run:
            return destination
        copy_runtime(source, destination)
        return destination

    if mode == "copy" and _is_relative_to(destination, source):
        raise ValueError(
            "Copy destination is inside the source repository. "
            "Use another --project-dir, --mode symlink, or --update for an existing Git install."
        )

    if destination.exists() or destination.is_symlink():
        if not force:
            raise FileExistsError(
                f"Destination already exists: {destination}. "
                "Use --update to refresh it or --force to replace a non-Git copy."
            )

        if is_git_checkout(destination):
            raise RuntimeError(
                f"Destination is a Git checkout: {destination}. "
                "Refusing to delete .git; use --update instead."
            )

        if dry_run:
            return destination

        if mode == "copy" and destination.is_dir() and not destination.is_symlink():
            copy_runtime(source, destination)
            return destination

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
        description="Install or update IT Infrastructure Equipment Selection as a portable Agent Skill"
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
        "--update",
        action="store_true",
        help=(
            "Update an existing installation. Git installs use 'git pull --ff-only'; "
            "copy installs safely resync only managed runtime files."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Replace/sync an existing non-Git installation. Git checkouts are never deleted; "
            "use --update for them."
        ),
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
        update=args.update,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        action = "Would update" if args.update else "Would install"
    else:
        action = "Updated" if args.update else "Installed"
    print(f"{action} {SKILL_NAME} for {normalize_target(args.target)} at: {installed}")
    if not args.dry_run:
        print("Verify discovery in the target host before relying on the skill.")


if __name__ == "__main__":
    main()

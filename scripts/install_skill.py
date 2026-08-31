#!/usr/bin/env python3
"""Install or update this Agent Skill in a supported host discovery directory."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable
from validate_json_schemas import validate_catalog

SKILL_NAME = "it-infrastructure-equipment-selection"
INSTALL_MANIFEST = ".skill-install.json"
OFFICIAL_ORIGIN = "https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill"

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
    "schemas",
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


def skill_identity(path: Path) -> None:
    text = (path / "SKILL.md").read_text(encoding="utf-8") if (path / "SKILL.md").is_file() else ""
    header = text.split("---", 2)[1] if text.startswith("---\n") and len(text.split("---", 2)) == 3 else ""
    if re.findall(r"^name:\s*([^\n]+)$", header, re.M) != [SKILL_NAME]:
        raise RuntimeError(f"Installation is not {SKILL_NAME}: {path}")


def origin(path: Path) -> str:
    result = subprocess.run(["git", "-C", str(path), "remote", "get-url", "origin"],
                            check=True, capture_output=True, text=True)
    return result.stdout.strip().removesuffix(".git").rstrip("/").replace("git@github.com:", "https://github.com/")


def update_git_checkout(path: Path, *, dry_run: bool = False, trusted_origin: str | None = None) -> Path:
    """Safely fast-forward an existing Git-installed skill."""
    if not is_git_checkout(path):
        raise ValueError(f"Not a Git checkout: {path}")
    skill_identity(path)
    expected = (trusted_origin or OFFICIAL_ORIGIN).removesuffix(".git").rstrip("/").replace("git@github.com:", "https://github.com/")
    if origin(path) != expected:
        raise RuntimeError("Git origin differs from trusted source; verify the repository before updating")
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
        skill_identity(path)
    return path


def runtime_hashes(path: Path, entries: Iterable[str] = RUNTIME_ENTRIES) -> dict[str, str]:
    hashes = {}
    for entry in entries:
        source = path / entry
        if not source.exists() or source.is_symlink():
            raise RuntimeError(f"Incomplete or symlinked runtime entry: {entry}")
        for file in ([source] if source.is_file() else sorted(source.rglob("*"))):
            if "__pycache__" in file.parts or file.suffix == ".pyc":
                continue
            if file.is_symlink():
                raise RuntimeError(f"Managed runtime symlink: {file.relative_to(path)}")
            if file.is_file():
                hashes[file.relative_to(path).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return hashes


def validate_runtime(path: Path) -> dict[str, str]:
    skill_identity(path)
    hashes = runtime_hashes(path)
    if not re.fullmatch(r"\d+\.\d+\.\d+", (path / "VERSION").read_text().strip()):
        raise RuntimeError("Invalid runtime VERSION")
    json.loads((path / "schemas/catalog.json").read_text(encoding="utf-8"))
    errors = validate_catalog(path)
    if errors:
        raise RuntimeError("Runtime schema/example validation failed: " + "; ".join(errors))
    for script in (path / "scripts").glob("*.py"):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    return hashes


def check_copy_destination(destination: Path, *, force: bool = False) -> None:
    if not destination.exists():
        return
    skill_identity(destination)
    manifest = destination / INSTALL_MANIFEST
    if not manifest.is_file() or manifest.is_symlink():
        if not force:
            raise RuntimeError("Legacy copy has no trusted installation manifest; inspect it and use --force explicitly")
        return
    record = json.loads(manifest.read_text(encoding="utf-8"))
    if record.get("skill") != SKILL_NAME or record.get("manifest_version") != 1:
        raise RuntimeError("Invalid installation manifest identity/version")
    if not force and runtime_hashes(destination) != record.get("files"):
        raise RuntimeError("Managed installation has local changes; preserve them before an explicit --force update")


def copy_runtime(source: Path, destination: Path, entries: Iterable[str] = RUNTIME_ENTRIES) -> None:
    """Stage, validate, then replace with rollback; never delete live entries first."""
    if destination.is_symlink() or is_git_checkout(destination):
        raise RuntimeError("Refusing copy replacement of a symlink or Git checkout")
    if source.resolve() == destination.resolve() or _is_relative_to(source.resolve(), destination.resolve()) or _is_relative_to(destination.resolve(), source.resolve()):
        raise ValueError("Copy source/destination must not overlap")
    hashes = validate_runtime(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f".{destination.name}.update-", dir=destination.parent))
    staged, backup = work / "staged", work / "previous"
    try:
        if destination.exists():
            shutil.copytree(destination, staged, symlinks=True)
        else:
            staged.mkdir()
        for entry in entries:
            src, dst = source / entry, staged / entry
            if dst.exists() or dst.is_symlink():
                _remove_existing(dst)
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(src, dst)
        if validate_runtime(staged) != hashes:
            raise RuntimeError("Staged runtime checksum mismatch")
        manifest = staged / INSTALL_MANIFEST
        if manifest.is_symlink():
            raise RuntimeError("Refusing symlinked installation manifest")
        manifest.write_text(json.dumps({"manifest_version": 1, "skill": SKILL_NAME,
            "version": (source / "VERSION").read_text().strip(), "source": str(source),
            "source_origin": origin(source) if is_git_checkout(source) else None,
            "source_commit": subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip() if is_git_checkout(source) else None,
            "files": hashes}, indent=2), encoding="utf-8")
        if destination.exists():
            os.replace(destination, backup)
        try:
            os.replace(staged, destination)
        except BaseException:
            if backup.exists():
                os.replace(backup, destination)
            raise
    finally:
        # If rollback itself fails, preserve the recovery directory for the user.
        if not backup.exists() or destination.exists():
            shutil.rmtree(work)


def install_skill(
    source: Path,
    destination: Path,
    *,
    mode: str = "copy",
    force: bool = False,
    update: bool = False,
    dry_run: bool = False,
    trusted_origin: str | None = None,
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
            return update_git_checkout(source, dry_run=dry_run, trusted_origin=trusted_origin)
        raise ValueError(
            "Copy source and destination are the same directory. "
            "Run updates from an independent clone or release package."
        )

    if update and (destination.exists() or destination.is_symlink()):
        if destination.is_symlink():
            target = destination.resolve()
            if is_git_checkout(target):
                update_git_checkout(target, dry_run=dry_run, trusted_origin=trusted_origin or (origin(source) if is_git_checkout(source) and source != target else None))
                return destination
            if target == source:
                return destination
            raise RuntimeError(
                f"Symlink target is not a Git checkout: {target}. "
                "Update the source directory manually."
            )

        if is_git_checkout(destination):
            update_git_checkout(destination, dry_run=dry_run, trusted_origin=trusted_origin or (origin(source) if is_git_checkout(source) else None))
            return destination

        validate_runtime(source)
        check_copy_destination(destination, force=force)
        if _is_relative_to(source, destination.resolve()) or _is_relative_to(destination.resolve(), source):
            raise ValueError("Copy source/destination must not overlap")
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

        validate_runtime(source)
        check_copy_destination(destination, force=force)

        if dry_run:
            return destination

        if mode == "copy" and destination.is_dir() and not destination.is_symlink():
            copy_runtime(source, destination)
            return destination

        _remove_existing(destination)

    if dry_run:
        validate_runtime(source)
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        validate_runtime(source)
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
    parser.add_argument("--trusted-origin", help="Explicitly verified Git origin for a private fork")
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
        trusted_origin=args.trusted_origin,
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

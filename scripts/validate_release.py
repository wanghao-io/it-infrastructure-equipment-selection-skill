#!/usr/bin/env python3
"""Validate release-version, metadata and runtime manifest consistency."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must be semantic x.y.z")
    changelog = root / "CHANGELOG.md"
    release_notes = root / "RELEASE_NOTES.md"
    if changelog.exists() and f"## v{version}" not in changelog.read_text(encoding="utf-8"):
        errors.append("CHANGELOG missing current version")
    if release_notes.exists() and f"Skill v{version}" not in release_notes.read_text(encoding="utf-8"):
        errors.append("RELEASE_NOTES missing current version")
    metadata = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    top_keys = [line.split(":", 1)[0] for line in metadata.splitlines() if line and not line[0].isspace()]
    if any(key not in {"interface", "policy", "dependencies"} for key in top_keys):
        errors.append("agents/openai.yaml contains unsupported top-level metadata")
    if "  display_name:" not in metadata or "  short_description:" not in metadata:
        errors.append("agents/openai.yaml missing interface display metadata")
    if "$it-infrastructure-equipment-selection" not in metadata:
        errors.append("agents/openai.yaml default_prompt must invoke the skill explicitly")
    for required in (
        "SKILL.md", "scripts/contracts.py", "scripts/compare_server_quotes.py",
        "scripts/calculate_hci_failover.py", "references/server-quotation-workflow.md",
        "scripts/validate_json_schemas.py", "schemas/catalog.json",
        "references/real-project-validation.md",
        "scripts/infra_cli.py", "assets/tool-catalog.json",
        "references/schema-governance.md", "references/private-extensions.md",
        "schemas/v2/price-evidence.schema.json",
    ):
        if not (root / required).is_file():
            errors.append(f"missing runtime file: {required}")
    return errors


def main() -> None:
    errors = validate()
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"release metadata valid: v{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}")


if __name__ == "__main__":
    main()

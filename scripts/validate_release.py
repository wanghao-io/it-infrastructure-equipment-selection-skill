#!/usr/bin/env python3
"""Validate release-version, metadata and runtime manifest consistency."""

from __future__ import annotations

import re
from pathlib import Path

from extract_release_notes import ReleaseNotesError, extract_release_notes

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must be semantic x.y.z")
    changelog = root / "CHANGELOG.md"
    release_notes = root / "RELEASE_NOTES.md"
    if changelog.exists():
        try:
            extract_release_notes(changelog.read_text(encoding="utf-8"), version)
        except ReleaseNotesError as exc:
            errors.append(f"CHANGELOG current release section invalid: {exc}")
    else:
        errors.append("CHANGELOG missing")
    if release_notes.exists():
        release_text = release_notes.read_text(encoding="utf-8")
        lines = release_text.splitlines()
        if not lines or lines[0] != f"# IT Infrastructure Equipment Selection Skill v{version}":
            errors.append("RELEASE_NOTES first heading must match current version")
        release_versions = re.findall(
            r"^# IT Infrastructure Equipment Selection Skill v(\d+\.\d+\.\d+)$",
            release_text,
            flags=re.MULTILINE,
        )
        if release_versions != [version] or re.search(r"^## v\d+\.\d+\.\d+\b", release_text, re.MULTILINE):
            errors.append("RELEASE_NOTES must contain only the current release")
    else:
        errors.append("RELEASE_NOTES missing")
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
        "schemas/v2/price-evidence.schema.json", "scripts/extract_release_notes.py",
        "schemas/v2/server-rfq.schema.json", "assets/server-rfq-v2-example.json",
        "examples/decision-summary-demo.md", "tests/scenarios/v15-evaluations.json",
        "scripts/project_records.py", "scripts/validate_project_delivery.py", "scripts/drawio_tools.py",
        "schemas/project-evidence.schema.json", "schemas/project-delivery.schema.json",
        "schemas/acceptance-evidence.schema.json", "assets/project-evidence-example.json",
        "assets/project-delivery-example.json", "assets/acceptance-evidence-example.json",
        "references/project-evidence.md", "references/project-delivery.md",
        "references/acceptance-evidence.md", "references/drawio-delivery.md",
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

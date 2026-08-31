"""Small, read-only project consistency checks. Evidence truth stays external."""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path

from contracts import is_unresolved, strict_json_loads
from validate_json_schemas import validate

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ("project-evidence", "project-delivery", "acceptance-evidence")


def load_record(path: Path):
    if path.stat().st_size > 10_000_000:
        raise ValueError("record exceeds 10 MB limit")
    return strict_json_loads(path.read_text(encoding="utf-8-sig"))


def preflight(data, family):
    if family not in FAMILIES:
        raise ValueError("unsupported project record family")
    schema = json.loads((ROOT / "schemas" / f"{family}.schema.json").read_text())
    errors = validate(data, schema)
    if errors:
        raise ValueError("; ".join(errors))


def guarded_path(root: Path, manifest: dict, value: str | Path, *, write=False) -> Path:
    """Resolve explicit paths only; never enumerate a project to discover inputs."""
    root = root.resolve()
    target = (root / value).resolve()
    if target == root or root not in target.parents:
        raise ValueError("path escapes project root or names the root itself")
    for blocked in manifest["protected_paths"]:
        path = (root / blocked).resolve()
        if target == path or path in target.parents:
            raise ValueError("path is protected by the project manifest")
    if write:
        allowed = [(root / item).resolve() for item in manifest["allowed_output_paths"]]
        if not any(path in target.parents for path in allowed):
            raise ValueError("output is outside declared output directories")
        for source in manifest["sources"]:
            if target == (root / source["path"]).resolve():
                raise ValueError("output would overwrite a read-only source")
    return target


def write_new(path: Path, text: str, *, root: Path, manifest: dict) -> None:
    """Publish a complete new artifact, never overwrite a concurrently created file."""
    preflight(manifest, "project-evidence")
    target = guarded_path(root, manifest, path, write=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    guarded_path(root, manifest, path, write=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False) as f:
        temporary = Path(f.name)
        try:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        guarded_path(root, manifest, path, write=True)
        os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def check_record(data, family, *, project_root: Path | None = None, check_files=False):
    preflight(data, family)
    if check_files and family != "project-evidence":
        raise ValueError("--check-files applies only to a project-evidence source manifest")
    findings = []
    metrics = {}
    def add(path, code, severity="error"):
        findings.append({"path": path, "code": code, "severity": severity})
    def index(rows, name):
        result = {}
        for i, row in enumerate(rows):
            if row["id"] in result:
                add(f"$.{name}[{i}].id", "duplicate-id")
            result[row["id"]] = row
        return result

    if family == "project-evidence":
        sources = index(data["sources"], "sources")
        facts = index(data["facts"], "facts")
        if not sources or not facts:
            add("$", "empty-evidence-record", "warning")
        active = defaultdict(list)
        for i, source in enumerate(data["sources"]):
            if source.get("derived_from") and source["derived_from"] not in sources:
                add(f"$.sources[{i}]", "unknown-original-source")
            if not source["sha256"]:
                add(f"$.sources[{i}].sha256", "source-not-fingerprinted", "warning")
            seen, current = set(), source
            while current:
                if current["id"] in seen:
                    add(f"$.sources[{i}]", "cyclic-source-lineage")
                    break
                seen.add(current["id"])
                current = sources.get(current.get("derived_from"))
            if check_files:
                if project_root is None:
                    raise ValueError("--project-root is required with --check-files")
                path = guarded_path(project_root, data, source["path"])
                if not path.is_file():
                    add(f"$.sources[{i}]", "source-file-missing")
                elif source["sha256"]:
                    digest = hashlib.sha256()
                    with path.open("rb") as handle:
                        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                            digest.update(chunk)
                    if digest.hexdigest() != source["sha256"]:
                        add(f"$.sources[{i}]", "source-changed-since-baseline")
        for i, fact in enumerate(data["facts"]):
            path = f"$.facts[{i}]"
            source = sources.get(fact["source_id"])
            if source is None:
                add(path, "unknown-source")
            elif fact["status"] == "known" and fact["field"] not in source["authority_fields"]:
                add(path, "source-not-authoritative-for-field")
            if fact["status"] == "known" and is_unresolved(fact["value"]):
                add(path, "known-fact-has-unknown-value")
            if fact["status"] in {"assumed", "unresolved"}:
                add(path, "fact-not-confirmed", "warning")
            if fact["status"] != "superseded":
                active[(fact["entity_id"], fact["field"])].append(fact)
            for old_id in fact.get("supersedes", []):
                old = facts.get(old_id)
                if not old or (old["entity_id"], old["field"]) != (fact["entity_id"], fact["field"]):
                    add(path, "invalid-field-supersession")
                elif old["status"] != "superseded" or is_unresolved(fact.get("approval_ref")):
                    add(path, "supersession-needs-disposition-and-approval")
        for key, rows in active.items():
            if len({json.dumps(r["value"], sort_keys=True) for r in rows}) > 1:
                add("$.facts", "conflicting-active-facts")
        metrics["active_fact_fields"] = len(active)
    elif family == "project-delivery":
        assets = index(data["assets"], "assets")
        bom = index(data["bom"], "bom")
        index(data["links"], "links")
        index(data["representations"], "representations")
        index(data["capacity_checks"], "capacity_checks")
        if not assets:
            add("$.assets", "no-assets", "warning")
        by_asset = defaultdict(list)
        for i, row in enumerate(data["bom"]):
            if row["asset_id"] is not None:
                by_asset[row["asset_id"]].append(row)
                asset = assets.get(row["asset_id"])
                if not asset:
                    add(f"$.bom[{i}]", "unknown-asset")
                elif any(row[k] != asset[k] for k in ("model", "phase_id", "disposition")):
                    add(f"$.bom[{i}]", "asset-bom-scope-mismatch")
            if row["quantity"] is None:
                add(f"$.bom[{i}].quantity", "quantity-unknown", "warning")
        for key, asset in assets.items():
            rows = by_asset[key]
            if asset["quantity"] is None or asset["model"] is None or asset["endpoint_ports"] is None:
                add("$.assets", "asset-fields-unknown", "warning")
            if asset["endpoint_ports"] and not any(key in (link["source"], link["target"]) for link in data["links"]):
                add("$.assets", "network-asset-has-no-declared-link", "warning")
            if asset["disposition"] == "buy" and (not rows or any(r["quantity"] is None for r in rows)
                    or sum(r["quantity"] or 0 for r in rows) != asset["quantity"]):
                add("$.bom", "purchased-asset-quantity-mismatch")
        for i, view in enumerate(data["representations"]):
            if view["baseline_id"] != data["baseline_id"]:
                add(f"$.representations[{i}]", "stale-artifact-baseline")
            seen = set()
            for row in view["devices"]:
                asset = assets.get(row["asset_id"])
                if row["asset_id"] in seen:
                    add(f"$.representations[{i}]", "duplicate-asset-projection")
                seen.add(row["asset_id"])
                if not asset or any(row[k] != asset[k] for k in ("quantity", "model", "phase_id", "disposition")):
                    add(f"$.representations[{i}]", "artifact-asset-mismatch")
            if seen != set(assets):
                add(f"$.representations[{i}]", "artifact-asset-coverage-mismatch")
        demands = defaultdict(float)
        lengths = {}
        for i, link in enumerate(data["links"]):
            if link["source"] not in assets or link["target"] not in assets:
                add(f"$.links[{i}]", "unknown-link-endpoint")
            if is_unresolved(link["protocol"]):
                add(f"$.links[{i}].protocol", "protocol-unknown-even-if-cable-known", "warning")
            for material in link["materials"]:
                if material["quantity"] is None:
                    add(f"$.links[{i}].materials", "material-quantity-unknown", "warning")
                else:
                    demands[material["bom_line_id"]] += material["quantity"]
            if "length" in link:
                length = link["length"]
                raw = sum(length[k] for k in ("path_m", "vertical_m", "termination_m", "detour_m"))
                lengths[link["id"]] = math.ceil(raw * (1 + length["waste_ratio"]) / length["round_to_m"]) * length["round_to_m"]
                if not length["unit_verified"] or length["basis"] != "surveyed-route":
                    add(f"$.links[{i}].length", "length-is-estimate-not-field-measurement", "warning")
        for i, dep in enumerate(data["dependencies"]):
            asset = assets.get(dep["asset_id"])
            if not asset or asset["quantity"] is None:
                add(f"$.dependencies[{i}]", "dependency-asset-unresolved")
            else:
                demands[dep["bom_line_id"]] += asset["quantity"] * dep["per_asset"]
        for line, demand in demands.items():
            if line not in bom or bom[line]["quantity"] is None or bom[line]["quantity"] < demand:
                add("$.bom", f"material-or-license-shortfall:{line}")
        capacities = {}
        for i, check in enumerate(data["capacity_checks"]):
            selected = [assets.get(key) for key in check["asset_ids"]]
            if not selected or any(a is None or a["quantity"] is None or (check["kind"] == "poe-watts" and a.get("power_w") is None) for a in selected):
                add(f"$.capacity_checks[{i}]", "capacity-input-unresolved", "warning")
                continue
            demand = sum(a["quantity"] * (a["power_w"] if check["kind"] == "poe-watts" else 1) for a in selected) * (1 + check["reserve_ratio"])
            capacities[check["id"]] = {"required": demand, "available": check["available"]}
            if check["available"] is None or is_unresolved(check["basis_ref"]):
                add(f"$.capacity_checks[{i}]", "capacity-evidence-unresolved", "warning")
            elif check["available"] < demand:
                add(f"$.capacity_checks[{i}]", "capacity-shortfall")
        known_ports = sum(a["endpoint_ports"] or 0 for a in assets.values())
        metrics.update(estimated_cable_lengths_m=lengths, capacity_checks=capacities,
                       known_endpoint_ports=known_ports,
                       declared_endpoint_ports=known_ports if all(a["endpoint_ports"] is not None for a in assets.values()) else None)
    else:
        index(data["records"], "records")
        if not data["records"]:
            add("$.records", "no-tests-recorded", "warning")
        for i, record in enumerate(data["records"]):
            path = f"$.records[{i}]"
            if record["result"] != "PASS":
                add(path, "test-not-passed", "warning")
                continue
            if not record["evidence_refs"] or any(is_unresolved(x) for x in record["evidence_refs"]):
                add(path, "pass-without-evidence")
            if record["adapter_used"] and is_unresolved(record["adapter_ref"]):
                add(path, "adapter-not-recorded")
            if record["claim"] == "native-compatibility" and (record["adapter_used"] or record["native_result"] != "PASS"):
                add(path, "adapter-or-non-native-result-cannot-prove-native-pass")
            if record["claim"] in {"field-acceptance", "business-recovery"} and (record["simulation_only"] or record["stage"] not in {"fat", "sat", "operation"}):
                add(path, "test-stage-cannot-prove-field-claim")
            if record["claim"] == "business-recovery" and record.get("business_recovery_confirmed") is not True:
                add(path, "boot-or-installation-is-not-business-recovery")
            if record["claim"] == "all-points" and (record["expected_count"] is None or record["tested_count"] != record["expected_count"] or record["simulation_only"] or record["unverified"]):
                add(path, "sample-or-simulation-cannot-prove-all-points")
            if record["unverified"]:
                add(path, "test-has-unverified-scope", "warning")
        ledger = data.get("point_ledger")
        if ledger:
            if any(value is None for value in ledger.values()):
                add("$.point_ledger", "point-count-basis-unresolved", "warning")
            if ledger["declared_source_count"] is not None and ledger["actual_source_count"] is not None and ledger["declared_source_count"] != ledger["actual_source_count"]:
                add("$.point_ledger", "source-export-count-mismatch")
            for upper, lower in (("mapped_io", "good_io"), ("historical_target", "historical_tested")):
                if ledger[upper] is not None and ledger[lower] is not None and ledger[lower] > ledger[upper]:
                    add("$.point_ledger", f"impossible-coverage-count:{lower}")
            for large, small in (("required_business_io", "mapped_io"), ("mapped_io", "good_io"), ("historical_target", "historical_tested")):
                if ledger[large] is not None and ledger[small] is not None and ledger[small] < ledger[large]:
                    add("$.point_ledger", f"coverage-incomplete:{small}", "warning")
            if all(ledger[k] is not None for k in ("required_business_io", "charged_system_points", "license_capacity")):
                if ledger["license_capacity"] < ledger["required_business_io"] + ledger["charged_system_points"]:
                    add("$.point_ledger", "production-license-capacity-shortfall")
        license = data.get("license")
        if license:
            if license["perpetual"] and license["expires_on"] is not None:
                add("$.license", "conflicting-license-term")
            if license["kind"] != "production" or is_unresolved(license["evidence_ref"]):
                add("$.license", "production-license-not-proven", "warning")
            if license["expires_on"] and date.fromisoformat(license["expires_on"]) < date.fromisoformat(data["as_of_date"]):
                add("$.license", "license-expired")
            if not license["perpetual"] and license["expires_on"] is None:
                add("$.license", "license-term-unknown", "warning")
    status = "FAIL" if any(f["severity"] == "error" for f in findings) else "CONDITIONAL" if findings else "PASS"
    return {"status": status, "scope": "declared-record-consistency-only", "findings": findings,
            "metrics": metrics, "procurement_ready": False, "field_acceptance_certified": False}

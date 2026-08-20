#!/usr/bin/env python3
"""Requirement-driven architecture decision helper.

This script does not select products. It converts explicit project facts into
architecture requirements/warnings so the solution does not add complexity by
default.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from contracts import is_unresolved, require_bool, require_int, strict_json_dumps, strict_json_loads


def evaluate(req: Dict[str, Any]) -> Dict[str, Any]:
    unresolved_fields: list[str] = []

    def tri_bool(key: str) -> bool | None:
        if key not in req or is_unresolved(req.get(key)):
            unresolved_fields.append(key)
            return None
        return require_bool(req[key], key)

    def tri_int(key: str, *, minimum: int = 0) -> int | None:
        if key not in req or is_unresolved(req.get(key)):
            unresolved_fields.append(key)
            return None
        return require_int(req[key], key, minimum=minimum)

    availability = None if is_unresolved(req.get("availability")) else str(req["availability"]).lower()
    if availability is None:
        unresolved_fields.append("availability")
    virtualization = tri_bool("virtualization_required")
    explicit_hci = tri_bool("hci_required")
    workload_count = tri_int("workload_count", minimum=0)
    server_count = tri_int("server_count", minimum=1)
    redundant_switching = tri_bool("redundant_switching_required")
    access_switches = tri_int("access_switch_count", minimum=0)
    high_speed_aggregation = tri_bool("high_speed_aggregation_required")
    vlan_count = tri_int("vlan_count", minimum=1)
    inter_vlan = tri_bool("inter_vlan_communication_required")
    external = tri_bool("external_network_interconnection")
    remote_access = tri_bool("remote_access_required")
    cross_trust = tri_bool("cross_trust_zone_connection")
    domestic = tri_bool("domestic_xinchuang_required")
    remote_control = tri_bool("ot_remote_control")

    if explicit_hci:
        hci = "required"
        hci_reason = "Explicit project/tender requirement."
    elif None in (explicit_hci, virtualization, availability, workload_count):
        hci = "unresolved"
        hci_reason = "HCI need cannot be decided until explicit HCI, virtualization, availability and workload facts are known."
    elif virtualization and availability in {"high", "zero-downtime", "mission-critical"} and workload_count >= 4:
        hci = "consider"
        hci_reason = "Virtualized multi-workload environment with high availability target; compare HCI with other HA architectures."
    else:
        hci = "not-required-by-current-requirements"
        hci_reason = "Virtualization/HA/scale requirements do not currently justify HCI."

    if redundant_switching is True or (access_switches is not None and access_switches > 1) or high_speed_aggregation is True:
        core = "consider-aggregation-or-core"
        core_reason = "Aggregation, redundancy, multi-access-switch scale or higher-speed backbone may justify a separate layer."
    elif None in (redundant_switching, access_switches, high_speed_aggregation):
        core = "unresolved"
        core_reason = "Aggregation/core need remains unresolved until switching scale, redundancy and backbone facts are explicit."
    else:
        core = "not-required-by-current-requirements"
        core_reason = "A single managed access switch can satisfy the stated scale if port/bandwidth capacity is adequate."

    if vlan_count is None:
        l3 = "unresolved"
        l3_reason = "VLAN count is unknown."
    elif vlan_count > 1 and inter_vlan is True:
        l3 = "required"
        l3_reason = "Multiple VLANs must communicate; a Layer-3 routing owner must be identified."
    elif vlan_count > 1 and inter_vlan is False:
        l3 = "not-required-if-vlans-remain-isolated"
        l3_reason = "VLAN separation alone is Layer 2; routing is only needed for cross-VLAN communication."
    elif vlan_count == 1:
        l3 = "not-required"
        l3_reason = "No cross-VLAN routing requirement is stated."

    else:
        l3 = "unresolved"
        l3_reason = "Inter-VLAN communication intent is unknown."

    if external is True or remote_access is True or cross_trust is True:
        firewall = "evaluate-required-boundary-control"
        firewall_reason = "External/remote/cross-trust connectivity requires explicit boundary security evaluation."
    elif external is False and remote_access is False and cross_trust is False:
        firewall = "not-required-by-current-isolated-scope"
        firewall_reason = "No external or cross-trust interconnection is stated; reassess before future interconnection."

    else:
        firewall = "unresolved"
        firewall_reason = "Connectivity/trust-boundary facts are incomplete; absence of input is not proof of isolation."

    single_server = server_count == 1 if server_count is not None else None
    single_server_controls = {
        "raid": "required" if single_server is True else "evaluate",
        "ups_graceful_shutdown": "required" if single_server is True else "evaluate",
        "independent_backup": "required" if single_server else "required",
        "single_point_of_failure_warning": single_server if single_server is not None else "unresolved",
    }

    remote_control_controls = None
    if remote_control is True:
        remote_control_controls = {
            "control_path": "SCADA command request -> PLC/equipment permissive logic -> equipment feedback",
            "required_controls": [
                "role_based_access",
                "second_confirmation_where_consequential",
                "operation_audit",
                "local_interlocks_preserved",
                "command_result_feedback",
                "failed_command_handling",
            ],
        }
    elif remote_control is None:
        remote_control_controls = {"status": "unresolved", "reason": "OT remote-control requirement is unknown."}

    return {
        "hci": {"decision": hci, "reason": hci_reason},
        "aggregation_core": {"decision": core, "reason": core_reason},
        "layer3_routing": {"decision": l3, "reason": l3_reason},
        "firewall": {"decision": firewall, "reason": firewall_reason},
        "domestic_xinchuang": {
            "decision": "required" if domestic is True else "not-required-by-current-requirements" if domestic is False else "unresolved",
            "reason": "Apply only when explicitly required by project, policy, tender or compatibility constraints.",
        },
        "single_server_controls": single_server_controls,
        "ot_remote_control": remote_control_controls,
        "input_status": "CONDITIONAL" if unresolved_fields else "PASS",
        "unresolved_fields": sorted(set(unresolved_fields)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate requirement-driven infrastructure architecture decisions")
    parser.add_argument("input", type=Path, help="JSON requirements file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    data = strict_json_loads(args.input.read_text(encoding="utf-8"))
    result = evaluate(data)
    print(strict_json_dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

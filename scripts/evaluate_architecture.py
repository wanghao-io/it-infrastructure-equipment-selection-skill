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

from contracts import optional_bool


def evaluate(req: Dict[str, Any]) -> Dict[str, Any]:
    availability = str(req.get("availability", "standard")).lower()
    virtualization = optional_bool(req.get("virtualization_required"), "virtualization_required")
    explicit_hci = optional_bool(req.get("hci_required"), "hci_required")
    workload_count = int(req.get("workload_count", 1) or 1)
    single_server = int(req.get("server_count", 1) or 1) == 1
    redundant_switching = optional_bool(req.get("redundant_switching_required"), "redundant_switching_required")
    access_switches = int(req.get("access_switch_count", 1) or 1)
    high_speed_aggregation = optional_bool(req.get("high_speed_aggregation_required"), "high_speed_aggregation_required")
    vlan_count = int(req.get("vlan_count", 1) or 1)
    inter_vlan = optional_bool(req.get("inter_vlan_communication_required"), "inter_vlan_communication_required")
    external = optional_bool(req.get("external_network_interconnection"), "external_network_interconnection")
    remote_access = optional_bool(req.get("remote_access_required"), "remote_access_required")
    cross_trust = optional_bool(req.get("cross_trust_zone_connection"), "cross_trust_zone_connection")
    domestic = optional_bool(req.get("domestic_xinchuang_required"), "domestic_xinchuang_required")
    remote_control = optional_bool(req.get("ot_remote_control"), "ot_remote_control")

    if explicit_hci:
        hci = "required"
        hci_reason = "Explicit project/tender requirement."
    elif virtualization and availability in {"high", "zero-downtime", "mission-critical"} and workload_count >= 4:
        hci = "consider"
        hci_reason = "Virtualized multi-workload environment with high availability target; compare HCI with other HA architectures."
    else:
        hci = "not-required-by-current-requirements"
        hci_reason = "Virtualization/HA/scale requirements do not currently justify HCI."

    if redundant_switching or access_switches > 1 or high_speed_aggregation:
        core = "consider-aggregation-or-core"
        core_reason = "Aggregation, redundancy, multi-access-switch scale or higher-speed backbone may justify a separate layer."
    else:
        core = "not-required-by-current-requirements"
        core_reason = "A single managed access switch can satisfy the stated scale if port/bandwidth capacity is adequate."

    if vlan_count > 1 and inter_vlan:
        l3 = "required"
        l3_reason = "Multiple VLANs must communicate; a Layer-3 routing owner must be identified."
    elif vlan_count > 1:
        l3 = "not-required-if-vlans-remain-isolated"
        l3_reason = "VLAN separation alone is Layer 2; routing is only needed for cross-VLAN communication."
    else:
        l3 = "not-required"
        l3_reason = "No cross-VLAN routing requirement is stated."

    if external or remote_access or cross_trust:
        firewall = "evaluate-required-boundary-control"
        firewall_reason = "External/remote/cross-trust connectivity requires explicit boundary security evaluation."
    else:
        firewall = "not-required-by-current-isolated-scope"
        firewall_reason = "No external or cross-trust interconnection is stated; reassess before future interconnection."

    single_server_controls = {
        "raid": "required" if single_server else "evaluate",
        "ups_graceful_shutdown": "required" if single_server else "evaluate",
        "independent_backup": "required" if single_server else "required",
        "single_point_of_failure_warning": single_server,
    }

    remote_control_controls = None
    if remote_control:
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

    return {
        "hci": {"decision": hci, "reason": hci_reason},
        "aggregation_core": {"decision": core, "reason": core_reason},
        "layer3_routing": {"decision": l3, "reason": l3_reason},
        "firewall": {"decision": firewall, "reason": firewall_reason},
        "domestic_xinchuang": {
            "decision": "required" if domestic else "not-required-by-current-requirements",
            "reason": "Apply only when explicitly required by project, policy, tender or compatibility constraints.",
        },
        "single_server_controls": single_server_controls,
        "ot_remote_control": remote_control_controls,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate requirement-driven infrastructure architecture decisions")
    parser.add_argument("input", type=Path, help="JSON requirements file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    result = evaluate(data)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

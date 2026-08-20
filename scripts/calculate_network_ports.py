#!/usr/bin/env python3
"""Network port planning and basic Layer-3 requirement helper."""

from __future__ import annotations

import argparse
import json
import math

from contracts import require_bool, require_float, require_int, strict_json_dumps


def calculate(
    endpoints: int,
    uplinks: int = 0,
    management_ports: int = 0,
    spare_ratio: float = 0.20,
    vlan_count: int = 1,
    inter_vlan_communication_required: bool = False,
) -> dict:
    endpoints = require_int(endpoints, "endpoints", minimum=0)
    uplinks = require_int(uplinks, "uplinks", minimum=0)
    management_ports = require_int(management_ports, "management_ports", minimum=0)
    spare_ratio = require_float(spare_ratio, "spare_ratio", minimum=0, maximum=10)
    vlan_count = require_int(vlan_count, "vlan_count", minimum=1)
    inter_vlan_communication_required = require_bool(
        inter_vlan_communication_required, "inter_vlan_communication_required"
    )

    downlink_base = endpoints + management_ports
    spare = math.ceil(downlink_base * spare_ratio)
    required_downlinks = downlink_base + spare
    base = downlink_base + uplinks
    required = required_downlinks + uplinks

    if required_downlinks <= 24:
        switch_port_class = 24
    elif required_downlinks <= 48:
        switch_port_class = 48
    else:
        switch_port_class = None

    l3_required = vlan_count > 1 and inter_vlan_communication_required

    return {
        "base_ports": base,
        "downlink_base_ports": downlink_base,
        "uplink_ports": uplinks,
        "spare_ports": spare,
        "required_ports": required,
        "required_downlink_ports": required_downlinks,
        "single_switch_port_class": switch_port_class,
        "multiple_switches_or_larger_platform_required": switch_port_class is None,
        "candidate_port_layout_confirmation_required": uplinks > 0,
        "port_layout_note": "The 24/48 class applies to downlinks. Confirm separate/shared uplink cages, media, speed, stacking and licensing on the exact candidate.",
        "vlan_count": vlan_count,
        "layer3_routing_required": l3_required,
        "routing_note": (
            "Identify the Layer-3 routing owner (L3 access switch, aggregation/core, router or firewall)."
            if l3_required
            else "Layer-3 routing is not required solely because VLANs exist; it is required when VLANs must communicate."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate network access port requirement")
    parser.add_argument("endpoints", type=int)
    parser.add_argument("--uplinks", type=int, default=0)
    parser.add_argument("--management-ports", type=int, default=0)
    parser.add_argument("--spare-ratio", type=float, default=0.20)
    parser.add_argument("--vlan-count", type=int, default=1)
    parser.add_argument("--inter-vlan", action="store_true")
    args = parser.parse_args()

    print(strict_json_dumps(calculate(
        args.endpoints,
        args.uplinks,
        args.management_ports,
        args.spare_ratio,
        args.vlan_count,
        args.inter_vlan,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

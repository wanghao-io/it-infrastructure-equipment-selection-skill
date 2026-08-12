#!/usr/bin/env python3
"""Network port planning and basic Layer-3 requirement helper."""

from __future__ import annotations

import argparse
import json
import math


def calculate(
    endpoints: int,
    uplinks: int = 0,
    management_ports: int = 0,
    spare_ratio: float = 0.20,
    vlan_count: int = 1,
    inter_vlan_communication_required: bool = False,
) -> dict:
    if min(endpoints, uplinks, management_ports) < 0:
        raise ValueError("port counts must be >= 0")
    if spare_ratio < 0:
        raise ValueError("spare_ratio must be >= 0")
    if vlan_count < 1:
        raise ValueError("vlan_count must be >= 1")

    base = endpoints + uplinks + management_ports
    spare = math.ceil(base * spare_ratio)
    required = base + spare

    if required <= 24:
        switch_port_class = 24
    elif required <= 48:
        switch_port_class = 48
    else:
        switch_port_class = None

    l3_required = vlan_count > 1 and inter_vlan_communication_required

    return {
        "base_ports": base,
        "spare_ports": spare,
        "required_ports": required,
        "single_switch_port_class": switch_port_class,
        "multiple_switches_or_larger_platform_required": switch_port_class is None,
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

    print(json.dumps(calculate(
        args.endpoints,
        args.uplinks,
        args.management_ports,
        args.spare_ratio,
        args.vlan_count,
        args.inter_vlan,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

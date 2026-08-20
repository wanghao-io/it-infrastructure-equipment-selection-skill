# Network Sizing Reference

## Port Planning

Calculate separate pools before selecting a chassis or switch:

```text
downlink endpoint ports + downlink spare ports
uplink ports by speed/media/redundancy
out-of-band and stack/peer-link ports
```

Use `scripts/calculate_network_ports.py` for transparent planning. A 15–25% spare-port allowance can be used for early budgeting unless a known expansion plan provides a better figure.

The helper's aggregate port class is an early budget signal only. Do not conclude that a 48-port switch is insufficient merely because 48 copper endpoints plus two uplinks total 50: many products expose separate uplink cages. Confirm the candidate's physical port layout, shared-port restrictions, stacking use and licensed speeds.

## PoE planning

For each powered-device class record quantity, negotiated/maximum watts, cable/temperature derating if applicable and startup behavior.

```text
required_PoE_W = Σ(device_count × design_power_W) × (1 + reserve_ratio)
```

Use at least the project-specified reserve; 20% is an early estimate only when no better growth basis exists. Check per-port class, total switch PoE budget, power-supply combination and surviving PoE budget after the defined PSU/switch failure. An AP count or switch port count alone does not prove PoE eligibility.

Wireless AP quantity requires both coverage and capacity planning plus a site survey. Record wall/rack/metal obstruction, ceiling height, interference, client density, roaming, channel plan and production-device requirements; do not size solely from floor area.

## Interface Types

Select only the speeds required by endpoints and uplinks:

- 1GE / 2.5GE / 5GE
- 10GE
- 25GE
- 40GE
- 100GE

Include required RJ45/SFP/SFP+/SFP28/QSFP modules, DAC/AOC, fiber and patch cords in the BOM.

## Architecture Follows Scale

### Small / single-switch OT

A single managed access switch can be sufficient when port count, bandwidth and availability requirements fit one switch.

A separate core switch is not mandatory merely because the project is industrial.

### Multiple VLANs

VLAN creation is Layer 2 segmentation. If devices in different VLANs must communicate, identify the **Layer-3 routing owner**:

- L3-capable access switch;
- aggregation/core switch;
- router;
- another approved routing device.

Do not propose several VLANs that require communication while selecting a switch that cannot route between them.

### Medium / multi-switch network

Consider a separate L3 aggregation/core layer when one or more apply:

- multiple access switches need aggregation;
- 10/25GbE or higher backbone/server links are needed;
- redundant switching paths are required;
- routing/ACL scale exceeds access-switch capability;
- multiple workshops/buildings or a major expansion phase are involved.

Do not call an L3-capable access switch a core switch only because it performs inter-VLAN routing.

## VLAN Planning

Common logical groups may include:

- server / data acquisition;
- PLC / equipment control;
- operator stations;
- large-screen/read-only display;
- network management.

Only create the VLANs that improve manageability or policy separation for the actual project. Do not invent VLAN IDs or IP subnets unless the project requires detailed design.

## Upgrade Triggers

Re-evaluate the network architecture when:

- access ports become insufficient;
- additional access switches are introduced;
- higher-speed server/backbone links appear;
- redundancy is required;
- new external network interconnections are introduced;
- routing or policy requirements materially grow.

For overall architecture choice, load `references/architecture-decision.md`. For operational remote control, also load `references/ot-control-safety.md`.

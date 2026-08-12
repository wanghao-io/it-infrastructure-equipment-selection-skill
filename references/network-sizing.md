# Network Sizing Reference

## Port Planning

Calculate:

```text
endpoint ports + uplink ports + management/service ports + spare ports
```

Use `scripts/calculate_network_ports.py` for transparent planning. A 15–25% spare-port allowance can be used for early budgeting unless a known expansion plan provides a better figure.

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

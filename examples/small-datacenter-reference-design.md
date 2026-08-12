# Small Data Center / Server Room Reference Design

> An anonymized reference design for method demonstration. All capacities are project-specific.

## Scenario

A small data center or enterprise server room hosts virtualization, databases, file services, backup, monitoring and network/security infrastructure.

The project requires a balanced design across compute, storage, network, power, recovery and lifecycle cost. The Skill must compare architecture options rather than assuming HCI.

## Example inputs

- A few dozen virtual machines
- Mixed application and database workloads
- Central backup and monitoring
- 10/25GbE server uplinks under consideration
- Planned service growth
- Defined maintenance windows
- Limited rack space and power budget

## Architecture alternatives

### Option A — Standalone physical servers

Appropriate when workloads are few, appliance-like or have strict software/licensing constraints.

### Option B — Traditional virtualization + shared storage

Appropriate when centralized storage, familiar operational tooling or independent compute/storage scaling is preferred.

### Option C — Hyper-converged infrastructure

Appropriate when operational simplicity, integrated scaling and the selected workload/availability model justify it.

The Skill should calculate and compare these options rather than choosing one automatically.

## Design questions

1. How many physical cores and how much RAM are required at steady state and after a host failure?
2. What is the required usable storage after RAID/replication/EC, snapshots and growth reserve?
3. Does the workload require 10GbE or 25GbE, and how many redundant paths are justified?
4. What backup capacity and retention are required?
5. What UPS kW/kVA and runtime are required at the calculated load?
6. Which architecture has the best balance of cost, recovery, expansion and operational complexity?

## Expected Skill output

- Workload inventory and assumptions
- Capacity model
- Architecture comparison
- N+1 validation only if required
- Storage raw/usable calculation
- Network uplink and switch-port sizing
- UPS sizing
- Vendor/model comparison matrix
- BOM and budget range
- Vendor-neutral tender parameters
- Mermaid/Graphviz network topology

## Procurement notes

Do not compare server families by base model only. Normalize CPU, memory, drives, NICs, RAID/HBA, PSU, rails, support and virtualization/software costs. For HCI, include platform subscription/support and required network components.

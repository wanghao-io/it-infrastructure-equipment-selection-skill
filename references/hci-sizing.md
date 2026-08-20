# HCI Sizing and Architecture Decision

Use HCI only after availability, workload, maintenance and failure-domain requirements make it a justified candidate. A successful calculation does not prove that the project needs HCI.

## Architecture decision

Compare at least:

1. standalone servers with independent backup;
2. traditional virtualization with shared storage or supported replication;
3. HCI with explicit quorum, protection and network design.

Consider HCI when consolidation scale, recovery objectives, operational capability and supported lifecycle justify its distributed complexity. Do not use “three nodes” as a universal starting rule.

## Required inputs

- workload CPU, memory, effective storage, IOPS and east-west/network demand;
- platform overhead, CPU overcommit basis and resource reserves;
- node, disk, NIC, switch, rack and site failure scenarios;
- simultaneous maintenance-plus-failure requirement;
- quorum/witness placement and failure behavior;
- replica or erasure-coding policy, usable-capacity definition and rebuild reserve;
- rebuild performance/window and tolerated degraded duration;
- hardware/software support matrix, license term and expansion constraints;
- backup, recovery, monitoring and operator readiness.

Unknown protection, network or failure-domain evidence remains `CONDITIONAL`. Never enter `true` merely to make the calculator pass.

## Capacity sequence

1. Freeze workload demand without headroom.
2. Add platform overhead and documented reserve independently for CPU, memory, effective storage, IOPS and network.
3. Calculate remaining capacity after the requested node loss with `scripts/calculate_hci_failover.py`.
4. Verify storage protection, quorum and failure-domain behavior against versioned vendor evidence.
5. Verify sufficient free space and performance to rebuild while serving production demand.
6. Test loss of each relevant node, disk, link, switch and failure domain; include maintenance-plus-failure when required.
7. Check that surviving network paths can carry storage replication, rebuild and application traffic.
8. Compare operational complexity and TCO with the simpler alternatives.

`usable_storage_tb` in `hci-failover-v1` is the effective per-node capacity available under the already-selected protection policy. It is not raw disk capacity. If that meaning is not evidenced, the input is unresolved.

## Decision states

- `capacity_check_status=PASS`: the supplied arithmetic passes after the stated failure and reserves.
- `capacity_check_status=FAIL`: at least one calculated dimension is short.
- `final_design_status=CONDITIONAL`: arithmetic passes but support, quorum, protection, rebuild or failure-domain evidence still requires review.
- Final design may pass only in the engineering review; v1 calculator output never proves it by itself.

No score, lower price or TCO advantage can rescue a Mandatory failure.

## Output

Record architecture alternatives, adoption trigger, node count/configuration, workload and reserves, remaining resources after each failure, protection policy, quorum/witness, rebuild capacity/window, east-west topology, support evidence/date, licenses, result by dimension, final-design TBDs and expansion trigger.

## Examples

Positive: four nodes retain documented CPU, memory, effective storage, IOPS and network reserves after one-node loss; quorum, replica behavior, two-switch paths and rebuild capacity are supported by current evidence. Arithmetic passes, while the final engineering review records the supporting evidence.

Negative:

- Any CPU, memory, effective-storage, IOPS or network shortage fails N+1.
- Adequate arithmetic with unknown quorum, protection or failure-domain evidence remains `CONDITIONAL`.
- Capacity that works only before rebuild reserve is included fails the required degraded operation.
- Three nodes are not automatically acceptable when maintenance plus one failure is required.
- `check_n_plus_one()` is a deprecated arithmetic compatibility wrapper and must not be cited as procurement or final-design evidence.

A future tri-state HCI contract may encode evidence status directly. Do not break the frozen v1 contract by silently changing boolean meanings.

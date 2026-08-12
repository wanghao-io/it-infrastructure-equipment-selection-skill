# Architecture Decision Reference

Use this reference before selecting products. The purpose is to determine the **minimum architecture justified by the requirements**, not to promote a preferred topology.

## 1. Decision Principles

- Start from workload, availability, recovery, security, maintainability, expansion and budget.
- Distinguish **mandatory requirements** from preferences.
- Prefer the simplest architecture that satisfies mandatory requirements with reasonable lifecycle and supportability.
- Do not add HCI, HA, dual-core, firewall, shared storage, domestic/Xinchuang constraints or other complexity without a requirement that justifies it.
- If a simpler architecture creates a material single point of failure, state that risk and specify compensating controls.
- Mark unresolved architecture inputs as `TBD`; do not invent them.

## 2. Compute Architecture

### Standalone physical server

Usually reasonable when:

- one or a small number of tightly related workloads exist;
- planned downtime is acceptable;
- automatic failover is not required;
- budget and operational simplicity are important;
- recovery can rely on RAID, UPS, backup and documented restore procedures.

For a single-server production design, explicitly evaluate:

- RAID/controller protection;
- UPS and graceful shutdown;
- independent backup;
- spare-part/warranty response;
- recovery procedure and expected RTO/RPO.

### Traditional virtualization

Consider when:

- several logical workloads benefit from isolation;
- application compatibility supports virtualization;
- easier backup, snapshot, migration or lifecycle management is valuable.

Virtualization alone does **not** imply HCI or HA.

### HCI

Consider only when requirements justify distributed compute/storage, simplified cluster operations, scale-out growth or HA.

Do not recommend HCI merely because:

- there are virtual machines;
- there is SCADA/BI/database software;
- three servers can fit the budget.

For N+1 claims, verify that CPU, memory, storage capacity and performance remain acceptable after one node is lost.

### HA / dual-server

Consider when the business-defined RTO or interruption tolerance cannot be met by restore/restart on a single server.

Do not translate the word “important” into automatic HA. Ask for or infer cautiously from explicit availability targets.

## 3. Network Architecture

### One managed access switch

Can be sufficient when:

- endpoint count fits with spare ports;
- one location / one small OT system is involved;
- no redundant switching requirement exists;
- uplink bandwidth is modest;
- there is no multi-switch aggregation requirement.

### VLAN rule

VLANs are useful for separating broadcast and policy domains, but VLAN creation alone does not provide cross-VLAN communication.

If `VLAN count > 1` and devices in different VLANs must communicate, the design **must identify the Layer-3 routing owner**, for example:

- L3-capable access switch / light Layer-3 switch;
- aggregation/core switch;
- router;
- firewall.

Never propose multiple isolated VLANs that require communication without a routing function.

### L3 access / aggregation / core

A dedicated aggregation/core layer becomes useful when one or more are true:

- multiple access switches must aggregate;
- 10/25/40/100GbE server or backbone traffic is required;
- redundant paths or dual-core design is required;
- routing scale, ACL scale or dynamic routing exceeds access-switch capability;
- multiple buildings, workshops or major expansion phases are involved.

Do not call a single L3-capable access switch a “core switch” merely because it performs inter-VLAN routing.

## 4. Firewall / Security Gateway Decision

A dedicated firewall/security gateway should be evaluated when:

- OT connects to office IT, Internet, cloud or third-party networks;
- trust zones require policy enforcement and logging;
- remote access/VPN is required;
- regulatory or customer standards require boundary protection.

For a genuinely isolated small OT LAN with no external interconnection, a firewall may be outside current scope. State the assumption explicitly and reassess when an external connection is introduced.

## 5. Domestic/Xinchuang Decision

Apply domestic/Xinchuang constraints only when required by:

- tender/RFQ clauses;
- customer policy;
- regulatory/project policy;
- explicit compatibility requirements.

Then verify CPU architecture, OS, database, SCADA, drivers and management tools as a complete compatibility chain. Do not infer Xinchuang from the project being located in China.

## 6. UPS Decision

Select UPS class from the actual objective:

- **Short outage + graceful shutdown:** line-interactive / economical UPS can be appropriate if load, waveform and shutdown integration are supported.
- **Power-quality-sensitive / high availability / long runtime:** evaluate online double-conversion UPS and battery runtime requirements.

Always calculate both W and VA and state the required runtime objective.

## 7. Display / Large-Screen Decision

Prefer the least duplicated compute path:

1. built-in commercial display player/browser when compatible;
2. OPS module when local Windows/runtime compatibility is needed;
3. dedicated mini PC only when the display cannot reliably run the required dashboard.

Do not add both OPS and a separate mini PC without a specific reason.

## 8. Decision Output

For each material architecture choice, output:

| Decision | Requirement evidence | Recommended choice | Why | Cost/complexity avoided | Risk/trigger for upgrade |
|---|---|---|---|---|---|

Examples:

- HCI: not required by current availability target → standalone server.
- Core switch: not required for one 48-port access switch → L3-capable managed access switch.
- Firewall: deferred while OT remains isolated → reassess before IT/Internet interconnection.

## 9. Anti-patterns

Do not:

- equate virtualization with HCI;
- equate VLANs with routing;
- add dual-core switching without a redundancy target;
- add a firewall only to make a diagram look enterprise-grade;
- remove RAID/UPS/backup from a single-server design merely to reduce capex;
- copy an architecture from an example without recalculating the requirements.

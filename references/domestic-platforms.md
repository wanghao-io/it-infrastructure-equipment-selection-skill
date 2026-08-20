# Domestic / Xinchuang Compatibility

Use this route only when policy, tender, customer or compatibility requirements explicitly require a domestic/Xinchuang platform. Brand origin is not proof of end-to-end compatibility.

## Versioned compatibility chain

Validate every Mandatory link:

```text
CPU ISA and exact model
→ firmware / BMC
→ OS version and kernel
→ virtualization or container layer
→ database and middleware
→ application / SCADA exact version
→ PLC, OPC and specialist drivers
→ NIC, RAID, GPU and USB license devices
→ backup, security and management agents
```

For each link record:

- exact product and version;
- requirement source and whether it is Mandatory;
- official support matrix, certification, vendor statement or controlled PoC evidence;
- evidence date and lifecycle/support stage;
- `PASS`, `CONDITIONAL` or `FAIL`;
- blocker, evidence owner and next validation action.

Do not infer compatibility from a neighboring version, CPU family, Linux distribution name or generic “fully compatible” marketing page.

## Validation sequence

1. Freeze the required application, SCADA, database, driver and peripheral versions.
2. Identify CPU ISA and exact server/board configuration, firmware and expansion devices.
3. Verify OS/kernel certification for that hardware configuration.
4. Verify database, middleware and runtime support on the exact OS/ISA combination.
5. Verify the application and every PLC/OPC/special driver against the same chain.
6. Verify backup, endpoint security, monitoring, license dongles and management agents.
7. Execute a controlled PoC when documentary evidence is incomplete or the integration is operationally critical.
8. Record performance, failover, backup/restore and upgrade acceptance tests.
9. Compare price only after every Mandatory link passes.

## Evidence hierarchy

Prefer current official compatibility matrices and signed vendor/project evidence. Certification without versions is context only. A PoC supports only its tested hardware, versions, peripherals and workload; it does not prove untested upgrades.

## Tender rules

Specify capabilities, ISA/OS/application compatibility, evidence and acceptance tests. Do not create permanent vendor rankings. If a brand or catalog restriction is Mandatory, cite its policy/tender source separately from technical compatibility.

Required BOM scope may include firmware entitlement, OS subscription, database/middleware licenses, migration tools, drivers, backup/security agents, support and compatibility testing. A server hardware price alone is not the platform budget.

## Output fields

Record chain component, exact version, requirement, evidence type/source/date, lifecycle, status, blocker, PoC/acceptance step, owner, license/support scope and `eligible_for_pricing`.

## Examples

Positive: the exact CPU/server, firmware, OS kernel, database, SCADA release, OPC driver, RAID/NIC and backup agent are supported by current matrices or a scoped PoC, with upgrade and support terms recorded. The chain may pass.

Negative:

- A domestic CPU and OS with an unsupported PLC/SCADA driver fail the chain.
- A certified OS/database pair with an unknown application version remains `CONDITIONAL`.
- A generic “fully compatible” page without versions or test scope cannot produce PASS.
- A PoC on one OS/kernel cannot prove a later kernel upgrade.
- Lower price cannot rescue a broken compatibility link.

Keep unknowns explicit. Domestic hardware does not automatically mean application, peripheral or operational compatibility.

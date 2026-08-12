# IT Infrastructure Equipment Selection Skill v1.1.0

## Requirement-Driven Infrastructure Design

v1.1.0 turns the project from a basic equipment-selection workflow into a more complete engineering decision skill for IT infrastructure and industrial IT/OT projects.

The guiding principle is:

> Requirements first. Architecture second. Sizing third. Products last.

## Highlights

- Requirement-driven architecture decisions instead of forcing HCI, HA, core switching, firewalls or Xinchuang into every project
- Standalone server, virtualization, HCI, L2/L3/core and security-boundary decision guidance
- SCADA and historian sizing/licensing workflow
- OT remote-control safety rules for authorization, confirmation, PLC/equipment permissives, audit and command feedback
- Service-based server sizing for SCADA, historian, database, BI, Web and integration workloads
- Historian retention, RAID-aware storage, network-port and UPS sizing calculators
- Configuration-level BOM and Chinese project budget template
- Authoritative procurement research workflow separating technical evidence, current market price and historical comparable transactions
- Structured price-evidence normalization
- Project-specific vendor/model comparison with mandatory knockout gates and weighted scoring
- Vendor-neutral tender/RFQ specification generation
- Mermaid and Graphviz network topology generation
- Output profiles for quick selection, internal review, procurement/RFQ, detailed design, compliance and BOM/budget stages
- Additional anonymized reference designs for industrial SCADA, enterprise campus, healthcare IT and small data-center/server-room projects
- Engineering regression tests to prevent common architecture mistakes

## Engineering Rules Added

- Virtualization does not automatically imply HCI.
- Multiple VLANs that need to communicate must have an identified Layer-3 routing function.
- A standalone production server must explicitly evaluate single-point-of-failure risk and compensating controls such as RAID, UPS/graceful shutdown and independent backup.
- SCADA procurement should separate Runtime, Development, I/O point tiers, clients, Web, historian, alarm, report/API, drivers and maintenance instead of using a single “SCADA software” line item.
- Remote start/stop and other physical-control commands must not bypass PLC/equipment-side permissive, interlock or protection logic.
- Firewall sizing must use real protection performance where available, not only raw stateful throughput.
- Product and price comparisons must normalize exact configurations, licenses, accessories, support and implementation scope.

## Validation

GitHub Actions validates:

- Python syntax
- Engineering scenario regression tests
- Architecture-decision checks
- Sizing calculators
- Price-evidence normalization
- Vendor comparison
- Tender specification generation
- Mermaid topology generation
- Graphviz topology generation

## Upgrade Notes

No migration is required from v1.0.0. Existing users can update the skill directory and use the new references, calculators and output modes as needed.

## License

MIT License

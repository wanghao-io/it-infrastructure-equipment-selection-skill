# Changelog

## Unreleased — v1.1.0

### Added

- Requirement-driven architecture decision reference covering standalone servers, virtualization/HCI/HA, L2/L3/core switching, firewall boundaries, Xinchuang, UPS and large-screen compute choices
- `scripts/evaluate_architecture.py` for structured architecture sanity checks
- SCADA sizing/licensing reference covering point classes, historian sampling/retention, clients, Web publishing, drivers and commercial license breakdown
- OT remote-control safety reference covering permissions, second confirmation, PLC/equipment permissives, audit trail, command feedback and FAT/SAT scenarios
- Output profiles for quick selection, internal review, procurement/RFQ, detailed design, compliance and BOM/budget stages
- `scripts/calculate_historian.py`
- `scripts/calculate_network_ports.py`
- `scripts/calculate_budget.py`
- Structured price-evidence schema and `scripts/normalize_price_evidence.py`
- Chinese project budget CSV template
- Engineering scenario regression tests under `tests/scenarios/`
- Consolidated server workload and price-evidence example data
- Requirement-driven vendor/model comparison framework with hard gates and weighted scoring
- Vendor-neutral tender/RFQ specification generation workflow
- Logical network topology generation in Mermaid and Graphviz DOT
- Additional anonymized reference designs for enterprise campus, healthcare IT and small data center/server room projects
- Authoritative procurement research workflow for technical evidence, lifecycle, market pricing and comparable transaction records

### Changed

- Reworked server sizing to support consolidated service workloads instead of relying only on VM-count formulas
- Reworked storage sizing for RAID1/5/6/10, usable capacity and retention/headroom planning
- Reworked UPS sizing to calculate both W and VA and state runtime/graceful-shutdown assumptions
- Reworked network sizing so a single managed/L3-capable access switch is valid when project scale supports it; a core layer is not assumed
- Added explicit rule that multiple VLANs requiring communication need an identified Layer-3 routing function
- Expanded BOM checklist to cover server/storage/network/UPS/rack/cabling/workstations/displays/SCADA/OT/services and price-scope checks
- HCI, domestic/Xinchuang, HA, firewall and other specialized architecture patterns remain optional and requirement-driven rather than default recommendations
- README and Skill now expose project-stage output profiles and the stronger engineering decision flow
- CI now runs engineering regression tests plus sizing and evidence-normalization smoke tests

## v1.0.0

Initial release.

Features:

- IT infrastructure equipment selection workflow
- Server sizing guidance
- HCI planning guidance
- Network and security equipment selection guidance
- Storage and UPS sizing guidance
- Domestic platform compatibility analysis
- BOM and compliance templates
- Validation scripts

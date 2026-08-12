# Changelog

## v1.1.1 — 2026-08-12

### Fixed

- Exact current configuration quotations now take precedence over lower-match historical or generic model-family prices when deriving budget anchors.
- Added configuration-match scoring for highly configurable enterprise equipment so same-chassis listings are not treated as equivalent procurement configurations.
- Two or more exact current quotes now define the primary observed market range without being averaged together with weaker evidence tiers.
- A single exact current quote is treated as the primary anchor while explicitly recommending a second quote before fixing a procurement control price.
- Highly configurable equipment without exact current quotes now defaults to a range with `Estimated` / `Needs confirmation` rather than false-precision single-number pricing.
- Current-price requests now require live research when live search tools are available instead of relying on model memory, old project budgets or historical transaction data alone.
- E-commerce starting/base prices, unavailable offers, low-match configurations, incomplete commercial scope and disallowed used/refurbished offers are explicitly excluded from primary budget anchors.
- Market aggregators and price-history sources are now treated as context by default unless an exact seller/SKU/quote is independently verified.

### Added

- `references/exact-configuration-pricing.md`
- `references/live-price-research.md` for quotation-oriented current market research and batch BOM pricing
- `references/platform-compatibility.md` covering OpenAI Codex, Claude Code, GitHub Copilot, Gemini CLI and other Agent-Skills-compatible hosts
- `scripts/install_skill.py` for user/project installation into Codex, Claude Code, GitHub Copilot and Gemini CLI discovery locations
- Product-class-specific price research for `configurable-enterprise`, `fixed-sku` and `commodity-component` items
- China-market channel guidance covering manufacturer/authorized quotes, JD/Tmall official/enterprise channels, ZOL/market aggregators, price-history tools and government procurement context without hard-coding a single universal source ranking
- Price-evidence priority tiers for exact current formal quotes, exact current market quotes, highly matched current quotes, historical transactions, component models, generic listings and engineering estimates
- Weighted default server configuration-match model covering CPU, memory, SSD, HDD, RAID/PLP, NIC, PSU, warranty, tax and mandatory accessories
- `product_class`, `quote_mode`, orderability, commercial-scope and starting-price fields in the structured price-evidence model
- `anchor_eligible`, `anchor_exclusion_reasons`, `price_signal_role` and confidence-level outputs in `scripts/normalize_price_evidence.py`
- `--summary` mode in `scripts/normalize_price_evidence.py` to select the preferred budget anchor without blending weaker evidence tiers
- Pricing regression tests ensuring exact current quotes cannot be pulled down by cheaper historical, aggregator, bare-chassis or starting-price signals
- Cross-platform regression tests for portable `SKILL.md` frontmatter, host installation paths and runtime-file copying

### Changed

- Repositioned the project from a Codex-oriented skill to a portable Agent Skill with one shared engineering codebase.
- `SKILL.md` now includes portable `license: MIT` metadata and explicit host-capability fallback rules.
- `agents/openai.yaml` is documented as an optional OpenAI/Codex extension rather than a core runtime dependency.
- README now provides installation and verification guidance for Codex, Claude Code, GitHub Copilot and Gemini CLI.

## v1.1.0 — 2026-08-12

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

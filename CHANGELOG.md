# Changelog

## v1.2.2 — 2026-08-12

### Fixed

- Budget ranges whose lower bound is below the existing amount now pass the universal downward-revision technical-fit gate even when the range overlaps the old budget.
- Server quote identity fields must be non-empty strings; supplier independence remains normalized across case and whitespace variants.
- Removed the obsolete permissive numeric helper so procurement costs have one strict validation path.

### Tests

- Added a real CLI end-to-end procurement regression that executes server inquiry comparison, reuses the validated quotations for an existing-budget revision, and verifies five-dimensional HCI N+1 output.
- Strengthened regressions for unresolved commercial cost exclusion, overlapping downward ranges, normalized duplicate suppliers and invalid identity types.

## v1.2.1 — 2026-08-12

### Fixed

- Downward budget revisions for fixed SKUs and commodity components now require explicit `PASS` technical fit and `eligible_for_pricing=true`, matching the documented universal gate.
- Invalid or unresolved commercial costs such as `TBD`, negative values and non-numeric strings are excluded instead of silently becoming zero.
- Server quote independence is based on normalized supplier identity, so multiple quote numbers from one supplier count as one source.
- Server RFQs require a complete minimum configuration baseline, supplier/channel identity, deterministic as-of date and fresh, valid quotations.
- Negative or excessive risk reserves are rejected; current price evidence receives a default 90-day freshness check.
- Mandatory attribute markers such as `unknown` remain `CONDITIONAL`, and fractional HCI node counts are rejected.
- The three simulated project regressions now execute the actual deterministic requirement, HCI, TCO and budget-revision commands.
- README release-state wording now matches the published feature set.
- GitHub Actions now use immutable Node 24-based `checkout` and `setup-python` releases, eliminating Node 20 deprecation warnings.

## v1.2.0 — 2026-08-12

### Added

- Frozen server RFQ baseline, strict quote validation and independent-quote budget control range.
- Procurement-grade HCI N+1 validation across CPU, memory, storage, IOPS, network and failure domains.
- Shared strict input contracts for booleans, finite non-negative numbers, dates and currencies.
- Cross-platform CI matrix and tag/release validation workflow.

### Fixed

- Copy installations can no longer delete themselves during self-update; unrelated Git repositories are rejected.
- Unknown mandatory-gate statuses, negative weights and string booleans can no longer produce misleading PASS results.
- Mixed currencies, duplicate evidence, incomplete commercial scope, expired quotes and failed technical fit are excluded from budget anchors.
- BOM/TCO unresolved values remain incomplete instead of becoming zero or crashing; tender output is deterministic and topology rejects unknown zones.

### Changed

- Server price reductions require an explicit PASS technical gate plus complete commercial scope.
- OpenAI metadata now follows the current `interface` schema.
- Unix documentation consistently uses `python3`.

## v1.1.2 — 2026-08-12

### Fixed

- Existing-budget revisions now preserve the previous line-item amount when weaker evidence cannot justify a lower configurable-enterprise price.
- `SKILL.md` now makes the budget-revision guard mandatory for short requests such as “更新一下价格”, preventing agents from bypassing the deterministic evidence gate.
- Project-saved and user-provided current human quotations can be treated as strong evidence when channel, date, configuration match and commercial scope are captured, even without a public URL.
- Added a specification-first price gate: cheaper products cannot redefine mandatory technical requirements after price research begins.
- UPS price reductions now require W, VA, runtime and graceful-shutdown checks before a candidate is allowed to influence the budget.
- A nominal `1500VA` label no longer implies suitability when real output W, runtime data or shutdown integration is insufficient or unverified.
- Budget summaries no longer claim `tax included`, `delivered` or equivalent complete commercial scope unless those attributes are confirmed for all material lines relevant to the statement.

### Added

- `assess_budget_revision()` and `--existing-budget` / `--product-class` guard support in `scripts/normalize_price_evidence.py`.
- Deterministic UPS candidate assessment in `scripts/calculate_ups.py` with `eligible-for-pricing` / `not-eligible-for-pricing` results.
- Regression tests covering weak-evidence server budget reductions, saved exact quotations, dirty/unsafe installation updates, UPS real-power sizing, runtime verification and shared Skill pricing gates.

### Changed

- Existing Git-based Skill installations can be safely refreshed with `--update`; `--force` refuses to delete Git metadata.
- Copy-based updates synchronize managed runtime files while preserving unrelated local files.
- Pricing workflow is now explicitly ordered as: requirements → technical fit → evidence quality → price.

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

# Changelog

## v1.5.0 — 2026-08-20

### Added

- `server-rfq-v2`, an exact-procurement-object contract covering CPU identity, DIMM layout, storage media/count/endurance, RAID, NIC/optics, power, rails, service level and explicit commercial scope.
- Guarded `infra_cli.py` commands for requirement guidance, v2 server-quote comparison, strict price evidence and non-destructive migration.
- A one-page synthetic decision-summary demo and focused v1.5 safety regressions.

### Changed

- Firewall, HCI and domestic/Xinchuang references now define inputs, Mandatory gates, evidence, outputs and negative cases; network, Historian and OT guidance now covers PoE, physical uplink layout, mixed sampling classes and controlled external access.
- HCI v1 PASS now means arithmetic capacity PASS only; final-design eligibility remains CONDITIONAL until support, protection, quorum, rebuild and failure-domain evidence is reviewed.
- Long procurement references now provide quick paths, and the Router keeps only portable `name`/`description` trigger metadata.

### Fixed

- Budget revision now rejects mixed/conflicting product classes and requires a matching baseline currency, preventing policy override and cross-currency reductions.
- Architecture evaluation keeps absent availability, connectivity and architecture facts unresolved instead of defaulting them to false or one.
- JSON Schema and deterministic calculators reject NaN/Infinity; server resources round upward; storage/Historian/TCO factors are finite and range checked.
- The public scenario-template example now executes through the requirement guide, duplicate vendor names no longer cross-wire Mandatory gates, and server quote revisions select the newest eligible supplier record.
- BOM rendering preserves the union of fields, refuses accidental overwrite and validates the budget before an atomic output replacement.
- The industrial SCADA example no longer defaults to three-node HCI, firewall or DMZ architecture from generic high-reliability language.

### Validation

- Added contract, currency, product-class, non-finite number, rounding, architecture UNKNOWN, HCI claim, v2 RFQ, guarded CLI, BOM and example-invariant regressions.
- Retained the full Linux/macOS/Windows and Python 3.10/3.12 release matrix, clean archive installation and staged Agent Skills compatibility gate.

## v1.4.3 — 2026-08-15

### Fixed

- Release artifact transfer now uses immutable `upload-artifact` v7.0.1 and `download-artifact` v8.0.1 commits that run on Node 24, removing the deprecation annotation observed during the first v1.4.2 release-pipeline rehearsal.

### Tests

- Added a release-workflow regression that requires the pinned Node 24 artifact actions and rejects the previous Node 20 commits.

## v1.4.2 — 2026-08-15

### Added

- A complete Router/invariant regression suite that checks all references, user-facing scripts, high-risk modes, portable paths and minimum output profiles.
- A catalog classification for every bundled script, including public calculators, guarded commands, lifecycle tools, deferred interfaces and internal maintenance utilities.
- A current-version release-note extractor, reusable full-validation workflow and staged `gh skill publish --dry-run` compatibility gate.
- Four independent simulated forward validations covering a small office, SCADA/OT remote control, an existing server-budget challenge and HCI N+1/TCO, plus an evidence-gated v1.5 proposal.

### Changed

- `SKILL.md` is now a 196-line Router with twelve stable engineering invariants; detailed budget-revision and price-evidence procedures are loaded progressively from focused references.
- README now presents current capabilities, separate Agent and deterministic-CLI paths, copyable task recipes, v1/v2 Schema governance, private-extension boundaries and community entry points instead of historical version prose.
- `infra_cli.py list --all` explains why non-calculator scripts are guarded, deferred, lifecycle-only or internal without exposing them through the generic `run` command.
- GitHub Releases now publish only the requested `CHANGELOG.md` version section; `RELEASE_NOTES.md` contains only the current release while the changelog remains the cumulative history.

### Fixed

- Structured TCO and HCI inputs passed to `infra_cli.py` now resolve relative to the caller's working directory and receive automatic named-Schema preflight before calculation.
- Normal CLI input failures no longer expose Python tracebacks; `--debug` retains diagnostic behavior for maintainers.
- Tag releases can no longer publish before the complete Linux/macOS/Windows and Python 3.10/3.12 validation finishes, and the tag must remain the exact current `main` head at both metadata and publish gates.

### Validation

- Expanded the local suite to 137 tests, including CLI parity/preflight, Router reachability, release-note isolation and release-workflow structure.
- The four fresh-agent scenarios triggered no blocking violation; the record is explicitly a simulated workflow evaluation, not external adoption, current-price, procurement, settlement or operational evidence.

## v1.4.1 — 2026-08-14

### Fixed

- Multiple eligible quotations from one normalized supplier/channel no longer make the budget anchor depend on input order.
- Supplier quote revisions now select the newest eligible record; same-date records prefer complete commercial scope and then the conservative higher comparable cost.

### Tests

- Added forward/reverse ordering and newer-quote precedence regressions for supplier-level evidence deduplication.

## v1.4.0 — 2026-08-14

### Added

- A thin `infra_cli.py` discovery/dispatch layer for whitelisted deterministic calculators and named JSON contracts, with copyable examples and concise errors.
- Frozen v1 contract support plus versioned v2 price-evidence and project-retrospective schemas, a schema catalog compatibility policy and a non-destructive migration command.
- A scenario-template contract and an explicit private-extension manifest contract.
- A documented public-core/private-adapter/private-data boundary that forbids automatic private-data discovery and supplier-controlled decision fields.

### Changed

- Price-evidence v2 requires one decision scope and explicit technical-fit fields; caller-declared evidence levels are separated from system-derived evidence levels.
- Project-retrospective v2 requires structured operational measurements and scope normalization before forecast-versus-award/settlement comparisons.
- `SKILL.md` was reduced below the progressive-disclosure limit while routing schema governance and private extension details to focused references.
- Existing calculator scripts and formulas remain compatible; the unified CLI is an optional wrapper, not a replacement for Agent research or engineering judgment.

### Tests

- Added CLI parity/error tests, v1-to-v2 non-destructive migration checks, v2 golden examples, schema catalog governance checks and public/private boundary regressions.

## v1.3.1 — 2026-08-14

### Fixed

- Price anchors now fail closed for every product class unless technical fit is explicitly `PASS` and `eligible_for_pricing=true`.
- Multiple quote numbers from the same normalized supplier/channel count as one independent market source.
- Evidence carrying different decision-scope identifiers is rejected instead of being merged across BOM lines, products or projects.
- Price decisions support schema-first strict contract validation; unversioned input requires explicit legacy mode and emits a warning.
- Real-project retrospectives reject award, settlement or operational evidence claims that exceed the documented project stage or omit the corresponding structured record.

### Tests

- Added regressions for fixed-SKU fail-closed anchoring, supplier independence, decision-scope isolation, strict/legacy contract behavior and retrospective semantic evidence gates.
- The procurement workflow test now executes strict schema preflight before inquiry-derived budget revision and HCI output validation.

## v1.3.0 — 2026-08-14

### Added

- Versioned Draft 2020-12 JSON Schema contracts for price evidence, server RFQs, TCO, HCI failover and anonymized real-project retrospectives.
- A dependency-free schema preflight command, catalog validation, strict unknown-field handling and negative regression cases.
- Two anonymized real design-stage retrospectives covering manufacturing SCADA budget revision and phased smart-factory network design.
- A field-learning workflow that separates design baselines, current quotations, awards, settlements and operational measurements.

### Changed

- Structured examples now declare `schema_version: 1`, and copied Skill installations include the schema catalog.
- Real cases must not present design-budget movement as procurement forecast accuracy; public figures are rounded and sensitive identities removed.

### Tests

- Expanded the suite to 91 tests and added schema validation to the cross-platform CI and package smoke path.

## v1.2.3 — 2026-08-14

### Added

- Complete community entry points: Discussions routing, actionable contribution guide, support policy, Code of Conduct, private security reporting, PR template and structured Issue forms.
- Transparent governance, maintainer roles/vacancies, promotion criteria, succession rules and a reproducible release/recovery runbook.
- Transitional CODEOWNERS routing and automated community-health regression tests.

### Changed

- The repository now explicitly reports its current human bus factor as 1 instead of implying that documentation alone solves the ownership risk.
- README links directly to support, contribution, governance, maintainer and community channels.

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

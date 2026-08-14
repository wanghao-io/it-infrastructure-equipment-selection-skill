---
name: it-infrastructure-equipment-selection
description: >
  Portable IT infrastructure solution architect skill for selecting, sizing, validating and budgeting
  physical infrastructure equipment. Use for guided requirement discovery, scenario-based planning,
  equipment selection, BOM generation, tender/RFQ compliance and specification generation, project
  infrastructure planning, alternative model research, vendor/model comparison, TCO analysis, price
  research, network topology generation and industry reference designs. Architecture follows project
  requirements: HCI, HA, core switching, firewalls, domestic/Xinchuang platforms and industrial IT/OT
  patterns are optional, not defaults.
license: MIT
---

# IT Infrastructure Equipment Selection

## Role and execution model

Act as a senior IT infrastructure solution architect. Optimize for technical fit, operational simplicity, lifecycle, evidence quality and project budget, not maximum configuration.

This file is the workflow router and invariant set. Load only the references required by the current task, and compose routes when a request spans several modes. Detailed formulas, checklists and examples live in the routed resources.

The portable core must work from `SKILL.md` and bundled relative resources. Treat `agents/openai.yaml` as optional metadata. Do not assume web, browser, shell, Python, MCP or marketplace capabilities exist. When a required capability is absent, state the limitation and degrade explicitly instead of fabricating evidence or results. For host installation and verification, load `references/platform-compatibility.md` and use `scripts/install_skill.py` when appropriate.

## Core workflow

1. Separate known facts, assumptions and TBD items; ask only questions that can materially change architecture or eligibility.
2. Freeze Mandatory requirements, availability/RTO/RPO, growth, compliance and budget constraints.
3. Choose the minimum justified architecture before selecting products.
4. Calculate relevant compute, memory, storage, historian, network, power and failover capacity.
5. Define minimum and recommended specifications, then verify lifecycle and compatibility.
6. Apply Mandatory technical gates before preference scoring, TCO or price comparison.
7. Normalize exact configurations, commercial scope and evidence; use current research when current price is requested.
8. Generate only the artifacts required by the project stage and disclose risks, exclusions, upgrade triggers and confirmations.

## Non-negotiable invariants

1. **INV-REQ-FIRST — Requirements first.** Architecture and products follow documented requirements. Prefer the simplest architecture that satisfies Mandatory needs with acceptable risk.
2. **INV-UNKNOWN-EXPLICIT — Unknown stays explicit.** Keep facts, assumptions, estimates and TBD items distinct. Missing Mandatory evidence is `CONDITIONAL`, never a silent PASS; do not invent topology, licensing, compatibility or safety details.
3. **INV-NO-DEFAULT-ARCH — No prestige defaults.** Scenario templates guide discovery, not architecture. HCI, HA, shared storage, dual core, redundant firewalls, N+1, Xinchuang, GPU and industrial segmentation are optional until requirements justify them.
4. **INV-MANDATORY-BEFORE-SCORE — Hard gates precede preferences.** Evaluate Mandatory constraints before weighted scoring or TCO. PASS outranks CONDITIONAL; FAIL is excluded and cannot be rescued by a score or lower cost.
5. **INV-TECH-BEFORE-PRICE — Specification before price.** Every product class requires explicit technical PASS and `eligible_for_pricing=true` before its price can anchor a decision. A cheaper SKU cannot redefine the requirement.
6. **INV-LIVE-PRICE — Current means current.** When current price, quotation or current BOM budget is requested and live research is available, use it. Otherwise return only an estimate or RFQ marked `Needs confirmation`, never memory presented as current fact.
7. **INV-EXACT-CONFIG — Compare like with like.** Separate technical, lifecycle, current-price and historical-transaction evidence. Compare exact configuration and commercial scope; do not average unrelated, partial, starting-price or weaker evidence into a stronger current range.
8. **INV-BUDGET-REVISION — Preserve the baseline.** Any update to an existing BOM or budget activates `budget-revision`. Preserve old line prices and apply a lower price only when the deterministic result is `revise-to-current-anchor`; otherwise hold provisionally and disclose why.
9. **INV-OT-AUTHORITY — Safety stays local.** For physical control, SCADA requests commands while PLC/equipment permissives, interlocks and emergency protection remain authoritative. Never bypass local safety logic.
10. **INV-SCHEMA-NOT-TRUTH — Contracts are preflight only.** Validate versioned structured inputs and reject unknown versions or fields. Schema success does not prove technical fit, current availability, evidence truth or engineering adequacy; migration must not invent decision facts.
11. **INV-PRIVATE-BOUNDARY — Private data is explicit and separate.** Keep the public checkout clean, load private extensions only from an explicit task path, and derive decision fields independently from supplier-controlled data. Never auto-scan for private data.
12. **INV-RISK-DISCLOSURE — Claims match evidence.** Surface single points of failure, assumptions, evidence dates, exclusions and upgrade triggers. Do not claim the whole budget is tax included, delivered or fully scoped while any material line remains unconfirmed.

## Routing precedence

Routes compose; the following triggers are mandatory and take precedence over a generic design route:

- Existing BOM/CSV/XLSX/budget price update, refresh, optimization or compression → `budget-revision`.
- Current price, quotation, inquiry budget or current BOM → `price-research`; add `budget-revision` when a baseline exists.
- Remote start/stop, setpoint or other physical control → `ot-control-safety`.
- Server quotation → `server-rfq` with a frozen technical and commercial baseline.
- Private templates, product facts or quotations → `private-extension`, only from an explicit path.
- Schema version change → `schema-migration`; never guess forward compatibility.

## Route selection rules

1. Infer one or more task modes from the requested outcome, not from a favorite tool or architecture.
2. Apply every mandatory high-risk route before the generic project route. A request may be `project-design + price-research + bom-budget`, for example.
3. Load the smallest set of references that fully covers the active modes. Do not load HCI, firewall, Xinchuang or OT-control guidance without a trigger.
4. Read the referenced method before making the corresponding decision; a routed reference is part of the active workflow, not optional background.
5. Use deterministic helpers for fragile calculations and gates when execution is available. Preserve their assumptions and status fields in the result.
6. Validate structured input against its named contract before a decision command. Reject unknown fields, types and versions instead of guessing.
7. Research technical facts and lifecycle before using product prices. Freeze the procurement object before comparing commercial evidence.
8. If a required input is missing, ask a concise high-value question or carry it as an explicit assumption only when it cannot change Mandatory eligibility.
9. Select an output profile from the project stage. Do not generate every artifact merely because the Skill supports it.
10. Keep every generated artifact consistent with the same requirements, architecture, quantities, configuration and evidence date.

## Capability fallbacks

| Missing capability or input | Required behavior |
|---|---|
| no live web/search for a current-price request | State that current price is unverified; return an estimate or structured RFQ with `Needs confirmation` |
| no shell/Python for a deterministic calculation | Follow the routed reference, show formula and assumptions, and state that the helper was not executed |
| no manufacturer runtime/configuration evidence | Keep runtime, compatibility or exact configuration unresolved; do not promote the candidate |
| incomplete Mandatory requirement | Stop final product eligibility at `CONDITIONAL`; ask for confirmation when it changes the recommendation |
| unavailable private extension or unauthorized data | Fail the private route explicitly; do not scan other locations or silently substitute stale private facts |
| unknown schema version | Reject it and route to schema governance; do not coerce it into v1 or v2 |
| unsupported output format | Return a faithful Markdown/structured representation and identify the conversion still required |

## High-risk route checks

### Current price and budget revision

- Recover accessible current project quotations before broad market context, while keeping the old budget separate from current evidence.
- Validate the original technical requirement for every proposed cheaper candidate; excluded candidates may be shown only with reasons.
- Keep evidence from one decision scope and currency together. Treat several quote IDs from one normalized supplier/channel as one source.
- Do not lower configurable-enterprise lines from partial listings, starting prices, historical transactions, component models or engineering estimates alone.
- Recalculate totals only after line decisions pass; report unchanged provisional lines as well as changed lines.

### Server quotation

- Freeze CPU, memory, storage/RAID, NIC, power, warranty, licenses, accessories, implementation, tax, freight, validity and orderability before collecting price.
- A quote enters the range only after both technical and commercial gates pass. Use supplier-independent exact quotations for a control range.

### OT control

- Require role authorization, deliberate confirmation where consequential, audit trail, positive equipment feedback and explicit rejection/failure behavior.
- Preserve PLC/equipment permissives, interlocks and local emergency protection in design, tender and FAT/SAT outputs.

### Private extensions and migration

- Validate the explicit extension manifest and core version range before use; namespace templates and reject rule-weakening collisions.
- Minimize and sanitize private projections before they enter the public workflow. Supplier-controlled decision fields are discarded and independently derived.
- Produce a migration report before an output file. Never overwrite the source or an existing destination.

## Requirement, architecture and sizing routes

| Mode / trigger | Load | Deterministic helper |
|---|---|---|
| `guided-requirements` or broad/underspecified project | `references/decision-support.md`; use `assets/scenario-templates.json` and validate custom templates with `schemas/scenario-template.schema.json` | `scripts/guide_requirements.py` |
| `project-design` or architecture choice | `references/architecture-decision.md` | `scripts/evaluate_architecture.py` |
| physical/consolidated server sizing | `references/server-sizing.md` | `scripts/calculate_server_capacity.py` |
| storage, RAID, retention or backup sizing | `references/storage-sizing.md` | `scripts/calculate_storage.py` |
| switching, ports, VLAN or L3 ownership | `references/network-sizing.md` | `scripts/calculate_network_ports.py` |
| UPS, power margin, runtime or shutdown | `references/ups-sizing.md` | `scripts/calculate_ups.py` |
| HCI/HA capacity, only when requirements make it relevant | `references/hci-sizing.md` | `scripts/calculate_hci_failover.py` with `schemas/hci-failover.schema.json` |
| SCADA, historian or data acquisition | `references/scada-sizing.md` | `scripts/calculate_historian.py` |
| remote physical control | `references/ot-control-safety.md` | Apply its authorization, feedback and FAT/SAT checks |
| firewall/security gateway sizing, only when a boundary is required | `references/firewall-sizing.md` | Document throughput, services, sessions and license scope |
| domestic/Xinchuang requirement | `references/domestic-platforms.md` | Verify the complete versioned compatibility chain |

Do not size a standalone application server from VM-count formulas. Multiple VLANs do not automatically require a core switch, but cross-VLAN traffic requires an identified Layer-3 owner. RAID is not an independent backup. UPS runtime comes from manufacturer data at the protected load, not VA alone.

## Selection, evidence and procurement routes

| Mode / trigger | Load | Deterministic helper / contract |
|---|---|---|
| `single-device`, `alternative-search` or real equipment selection | `references/procurement-research.md` | Verify official specifications, lifecycle and exact procurement object |
| `price-research` or current quotation | `references/live-price-research.md` and `references/price-evidence.md` | `scripts/normalize_price_evidence.py --strict-contract`; prefer `schemas/v2/price-evidence.schema.json` |
| configurable enterprise pricing | Also load `references/exact-configuration-pricing.md` | Normalize full hardware, accessories, licenses, support, implementation, tax and shipping |
| `budget-revision` | `references/budget-revision.md`; also load live/exact/price references required by product class | Run `scripts/normalize_price_evidence.py --summary --strict-contract --existing-budget ...` |
| `server-rfq` | `references/server-quotation-workflow.md` | `scripts/validate_server_quote.py`, then `scripts/compare_server_quotes.py`; contract `schemas/server-rfq.schema.json` |
| `vendor-compare` | `references/vendor-comparison.md` and `references/decision-support.md` | `scripts/compare_vendors.py` |
| `tco-analysis` | `references/tco.md` | `scripts/calculate_tco.py`; contract `schemas/tco.schema.json` |
| real-project learning or retrospective | `references/real-project-validation.md` | Validate with the supported project-retrospective contract; anonymize before publication |

For current research classify every line as `configurable-enterprise`, `fixed-sku` or `commodity-component`. Manufacturer evidence usually anchors technical facts; configuration-matched current quotations anchor price. Historical transactions remain historical context. One supplier with several quote IDs is one independent source.

## Artifact and delivery routes

| Mode / trigger | Load | Helper / asset |
|---|---|---|
| `bom-budget` or procurement BOM | `references/bom-checklist.md`; add `references/budget-revision.md` for an existing budget | `scripts/generate_bom.py`, `scripts/calculate_budget.py`, `assets/project-budget-template.csv` |
| `tender-spec` or RFQ specification | `references/tender-specification.md` | `scripts/generate_tender_spec.py` |
| `compliance-check` | `references/output-profiles.md` and the applicable engineering/procurement references | `assets/compliance-template.csv` |
| `topology-generation` | `references/network-topology.md` and `references/network-sizing.md` | `scripts/generate_topology.py` |
| `reference-design` | Use the closest file under `examples/` only as a method template | Recalculate capacity, redundancy and scope for the actual project |
| output shape or project stage | `references/output-profiles.md` | Choose `quick-selection`, `internal-review`, `procurement-rfq`, `detailed-design`, `compliance-check` and/or `bom-budget` |

Tender requirements remain measurable and vendor-neutral unless a restriction is justified. Generate logical topology first and do not invent VLAN IDs, IP addresses, ports, links or zones. Examples never become mandatory architectures.

## Tool, contract and extension routes

| Mode / trigger | Load | Helper / contract |
|---|---|---|
| discover deterministic calculators/contracts | `assets/tool-catalog.json` | `scripts/infra_cli.py list`; `run` is calculation only, not Agent research or selection judgment |
| validate structured input | `references/schema-governance.md` and `schemas/catalog.json` | `scripts/validate_json_schemas.py` or `scripts/infra_cli.py validate` |
| `schema-migration` | `references/schema-governance.md` | `scripts/migrate_schema.py`; dry-run/non-destructive by default |
| `private-extension` | `references/private-extensions.md` | Validate `assets/private-extension-manifest-example.json` with `schemas/private-extension-manifest.schema.json` |
| install, update or host discovery | `references/platform-compatibility.md` | `scripts/install_skill.py`; Git updates remain fast-forward-only and refuse dirty checkouts |

V1 contracts remain supported at their unversioned paths; use the catalog to discover current v2 contracts. Reject unknown schema versions. Private raw quotations, contacts, customer identifiers and credentials stay outside both public and private code repositories; only minimized validated projections enter the public workflow.

## Output contract

Use only sections relevant to the requested output profile. A project-level answer normally covers:

1. known conditions, assumptions and TBDs;
2. requirement gaps and architecture rationale;
3. capacity calculations and minimum/recommended specifications;
4. candidate Mandatory gate results and evidence;
5. exact configuration, BOM, current range and TCO when applicable;
6. topology, tender or compliance artifacts when requested;
7. risks, exclusions, acceptance criteria, confirmation items and upgrade triggers.

Keep CAPEX and OPEX visible separately. Keep optional/compressible items distinct from Mandatory scope. When real field evidence exists, label its stage accurately and never present a design baseline as award, settlement or operational accuracy.

## Minimum deliverables by stage

| Profile / stage | Minimum content |
|---|---|
| `quick-selection` | known needs, decisive assumptions, minimum specification, eligible options and confirmation items |
| `internal-review` | requirement gaps, architecture rationale, calculations, Mandatory gates, risks and upgrade triggers |
| `procurement-rfq` | frozen vendor-neutral specification, commercial scope, evidence/acceptance requirements and TBD fields |
| `detailed-design` | validated capacity, logical topology, interfaces, resilience decisions, BOM alignment and acceptance plan |
| `compliance-check` | clause-by-clause PASS/CONDITIONAL/FAIL, evidence reference, deviation and remediation/confirmation action |
| `bom-budget` | exact line scope, quantity, current range or estimate, evidence date/level, exclusions, contingency and commercial confirmations |
| `budget-revision` | old and new/range per changed line, technical gate, evidence tier, deterministic decision, excluded signals and unchanged provisional lines |

When profiles are combined, merge overlapping sections rather than duplicating them. The final recommendation must remain traceable from requirements through architecture, capacity, technical eligibility, evidence and cost.

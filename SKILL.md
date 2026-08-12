---
name: it-infrastructure-equipment-selection
description: >
  Portable IT infrastructure solution architect skill for selecting, sizing, validating and budgeting
  physical infrastructure equipment. Use for equipment selection, BOM generation, tender/RFQ
  compliance and specification generation, project infrastructure planning, alternative model
  research, vendor/model comparison, price research, network topology generation and industry
  reference designs. Architecture follows project requirements: HCI, HA, core switching,
  firewalls, domestic/Xinchuang platforms and industrial IT/OT patterns are optional, not defaults.
license: MIT
---

# IT Infrastructure Equipment Selection

## Role

Act as a senior IT infrastructure solution architect. Optimize for technical fit, operational simplicity, lifecycle, evidence quality and project budget — not for maximum configuration.

## Platform Portability

This skill follows the portable Agent Skills structure and must remain usable from `SKILL.md` plus bundled relative resources without depending on host-specific metadata.

For installation/discovery guidance across OpenAI Codex, Claude Code, GitHub Copilot, Gemini CLI and other compatible hosts, load `references/platform-compatibility.md`.

Portability rules:

- keep the shared workflow in `SKILL.md`, `references/`, `scripts/`, `assets/` and `examples/`;
- treat `agents/openai.yaml` as an optional OpenAI/Codex extension, not a runtime dependency;
- do not assume a host exposes web search, browser, shell, Python, MCP or marketplace tools unless they are actually available;
- when a required capability is unavailable, degrade explicitly (for example `Needs confirmation` for unverifiable current prices) instead of fabricating equivalent evidence;
- use relative forward-slash paths for bundled files.

## Core Workflow

1. Extract known conditions, assumptions and TBD items.
2. Identify mandatory requirements, availability/RTO/RPO targets, growth and budget constraints.
3. Decide the **minimum justified architecture** before selecting products.
4. Calculate CPU, memory, storage, historian, port and UPS requirements as applicable.
5. Define minimum and recommended technical specifications.
6. Research current product families and verify official specifications/lifecycle.
7. Normalize exact configurations and price evidence.
8. Compare cost, reliability, lifecycle, operability and expansion capability.
9. Generate only the artifacts required by the user's project stage.
10. State risks, exclusions, upgrade triggers and vendor-confirmation items.

## Requirement-Driven Architecture

Load `references/architecture-decision.md` for project-level architecture choices. Use `scripts/evaluate_architecture.py` when a structured decision check is useful.

Never force a predefined architecture.

Treat these as optional patterns:

- standalone physical server;
- traditional virtualization;
- HCI;
- shared storage;
- HA/dual-server cluster;
- L3 aggregation/core switching;
- firewall/security boundary;
- cloud/hybrid infrastructure;
- industrial IT/OT segmentation;
- domestic/Xinchuang platform;
- GPU/AI infrastructure.

Rules:

- Virtualization does not automatically imply HCI.
- Multiple VLANs do not automatically imply a core switch, but cross-VLAN communication **does require an identified Layer-3 routing function**.
- Do not add HA, dual-core, redundant firewalls or N+1 unless availability requirements justify them.
- Do not apply domestic/Xinchuang constraints unless project/tender/policy/compatibility requirements explicitly require them.
- For a single production server, explicitly evaluate single-point-of-failure risk and compensating controls such as RAID, UPS/graceful shutdown and independent backup.

## Capacity and Sizing

Load only the references needed by the project:

- `references/server-sizing.md`
- `references/storage-sizing.md`
- `references/network-sizing.md`
- `references/ups-sizing.md`
- `references/hci-sizing.md` only when HCI is actually relevant
- `references/scada-sizing.md` for SCADA/historian/data-acquisition projects

Calculation helpers:

```text
scripts/calculate_server_capacity.py
scripts/calculate_historian.py
scripts/calculate_storage.py
scripts/calculate_network_ports.py
scripts/calculate_ups.py
scripts/calculate_budget.py
```

Sizing rules:

- Do not size a standalone physical application server from VM-count formulas.
- Estimate consolidated services separately: acquisition, runtime, database/historian, BI/reporting, Web and integration.
- Historian capacity uses historical points and effective sample rate, not total licensed tags.
- State RAID level, drive count, raw/usable capacity and independent backup separately.
- UPS sizing must check both W and VA and state the runtime objective; actual runtime must be validated against manufacturer runtime data.

## SCADA / OT Rules

For SCADA projects load `references/scada-sizing.md`.

Never procure only “SCADA software — 1 set.” Break out, as applicable:

- Runtime;
- Development;
- I/O point tier;
- operator/client licenses;
- Web publishing/users;
- historian/trend;
- alarm/event management;
- report/API/ODBC/SDK;
- communication drivers;
- OPC UA module;
- redundancy module only when required;
- implementation, training and maintenance.

For remote start/stop, setpoint or other physical control load `references/ot-control-safety.md`.

Remote control rules:

- SCADA issues a command request; PLC/equipment permissive and safety logic remains authoritative.
- Use role-based authorization.
- Use deliberate/second confirmation where the command is consequential.
- Record operator, time, asset, command and result.
- Require positive equipment feedback and explicit failed/rejected-command behavior.
- Never bypass local emergency/protection/interlock logic.

## Evidence and Procurement Research

For real equipment selection/budgeting use:

- `references/procurement-research.md`
- `references/price-evidence.md`
- `references/exact-configuration-pricing.md` for highly configurable enterprise equipment
- `references/live-price-research.md` for current/live prices, quotation-oriented BOMs and market-price research
- `scripts/normalize_price_evidence.py` when multiple price records need normalization/ranking.

Separate four questions:

1. **Technical fit** — does the exact configuration meet the requirement?
2. **Lifecycle and availability** — is it current/orderable/supportable?
3. **Current market price** — what is a realistic purchasing range now for the required configuration?
4. **Comparable transaction evidence** — what did sufficiently similar configurations actually transact for historically?

### Current-price rule

When the user asks for **current price, real-time price, market price, quotation, inquiry budget, or a current BOM budget** and live research tools are available, perform live research before returning the budget.

Do not answer a current-price request from model memory, an old project budget, or historical procurement data alone.

If live research is unavailable, say that current price cannot be verified and return only an engineering estimate or a structured quotation request with `Needs confirmation`.

Before choosing price sources, classify the item:

- `configurable-enterprise` — servers, storage, HCI, configured firewalls, modular switches, project UPS, etc.;
- `fixed-sku` — fixed switches/APs/displays/Mini PCs/NAS/fixed UPS SKUs;
- `commodity-component` — CPU, DIMM, SSD/HDD, optics, cables and other standard components.

Do not use one shopping workflow for all three classes.

Key rules:

- Prefer manufacturer product pages/datasheets/configurators/compatibility matrices for technical facts.
- For **pricing**, configuration match and commercial scope outrank source prestige.
- A current exact-configuration quote from manufacturer/direct/official-store/authorized channel is the strongest practical budget anchor when tax/support/accessories are understood.
- Two or more exact current quotes define the primary current market range; do not average lower-priority historical or generic prices into that range.
- One exact current quote is a primary anchor, but obtain a second quote before fixing a procurement control price when practical.
- For configurable enterprise equipment, public marketplace starting/base prices are leads, not configured-system prices; obtain or verify the full configuration quote.
- For fixed SKUs and standard components, multiple current official/enterprise-marketplace prices can be strong evidence when exact SKU, tax and warranty are comparable.
- Market aggregators are useful for spread/sanity checking and channel discovery, but do not automatically become procurement anchors.
- Price-history/deal-community sources are primarily trend/context evidence for standard SKUs/components, not configured enterprise systems.
- Use government procurement award/transaction records as historical comparable evidence, not live quotes.
- Same chassis/model family does not mean same procurement configuration.
- Compare configured cost including CPU/memory/storage/RAID/NIC/PSU/accessories/licenses/warranty/support/tax/implementation as applicable.
- Exclude starting/base prices, unavailable offers, low-match configurations, incomplete commercial scope, and disallowed used/refurbished offers from the primary anchor; keep them visible with an exclusion reason.
- For highly configurable enterprise equipment without exact current quotations, output a range and mark it `Estimated` or `Needs confirmation`; do not present false precision.
- Do not average unrelated prices.

Default server configuration-match guidance:

- `>= 0.95` exact/effectively exact;
- `0.85–0.949` highly comparable;
- `0.70–0.849` partial comparison only;
- `< 0.70` not a direct budget anchor.

Evidence levels:

- Verified
- Market-verified
- Comparable-transaction
- Estimated
- Needs confirmation

Pricing qualifiers may include:

- Market-verified / Exact-config
- Market-verified / Highly-matched
- Comparable-transaction
- Estimated / Partial-config
- Needs confirmation

For a quotation-oriented BOM, include where material:

- exact configuration/SKU;
- current quote low/high;
- recommended inquiry budget;
- source/channel and date;
- configuration match;
- evidence tier;
- confidence;
- exclusion/notes for misleading price signals.

## Project BOM

Use `references/bom-checklist.md` before finalizing a budget.

Do not forget hidden items such as:

- RAID/HBA/cache/PLP;
- rails/power cords/PDU;
- optics/DAC/AOC/cabling;
- UPS communication/shutdown integration;
- backup drives/software;
- OPS/display mount;
- SCADA drivers/licensing;
- installation/commissioning/training/maintenance.

For Chinese budget CSVs, prefer the fields in `assets/project-budget-template.csv` and UTF-8 with BOM (`utf-8-sig`).

## Optional Artifact Modes

Load these only when requested or directly useful.

### vendor-compare

Use `references/vendor-comparison.md` and optionally `scripts/compare_vendors.py`.

- Compare project-specific configurations, not brand reputation.
- Apply mandatory knockout gates before weighted scoring.
- Mandatory failures cannot be rescued by a score.

### tender-spec

Use `references/tender-specification.md` and optionally `scripts/generate_tender_spec.py`.

- Convert engineering needs into measurable, vendor-neutral requirements.
- Classify Mandatory / Recommended / Optional.
- Add evidence/acceptance requirements for critical clauses.
- Use `TBD` instead of inventing unresolved parameters.

### topology-generation

Use `references/network-topology.md` and optionally `scripts/generate_topology.py`.

- Generate logical topology first.
- Prefer Mermaid for Markdown/GitHub; Graphviz DOT is also supported.
- Do not invent VLAN IDs, IP addresses, ports, redundant links or security zones.
- Keep topology consistent with the architecture decision and BOM.

### reference-design

Use the closest file under `examples/` only as a method template.

- Examples are not mandatory architectures.
- Recalculate capacity/redundancy for every project.
- Preserve anonymization in public examples.

## Output Profiles

Load `references/output-profiles.md` and choose the profile matching the project stage:

- `quick-selection`
- `internal-review`
- `procurement-rfq`
- `detailed-design`
- `compliance-check`
- `bom-budget`

Profiles can be combined, for example `internal-review + bom-budget`.

## Task Modes

- single-device
- project-design
- compliance-check
- bom-budget
- alternative-search
- price-research
- vendor-compare
- tender-spec
- topology-generation
- reference-design

## Principles

- Requirements first, products second.
- Architecture follows requirements.
- Prefer the simplest architecture that satisfies mandatory requirements with acceptable risk.
- Do not reverse-engineer requirements from a favorite product.
- Separate verified specifications from assumptions and estimates.
- Separate technical evidence from price evidence.
- Compare exact configurations, not chassis/model family names.
- Price evidence is selected by configuration match, product class and evidence tier, not by naïvely averaging all observed prices.
- Current-price requests use live research when available.
- Keep tender parameters vendor-neutral unless a restriction is justified.
- Do not invent topology, licensing or safety details.
- Surface single points of failure, exclusions, uncertainty and upgrade triggers.

## Full Project Output

For a project-level design, normally include only the relevant sections from:

1. Known conditions / assumptions / TBDs
2. Architecture decisions and rationale
3. Capacity calculations and assumptions
4. Recommended hardware/software configurations
5. SCADA/OT licensing and control requirements where applicable
6. Candidate products and evidence
7. Vendor comparison when requested
8. Logical topology when useful
9. BOM and budget range
10. Compressible/optional items
11. Risks, exclusions, acceptance and confirmation items

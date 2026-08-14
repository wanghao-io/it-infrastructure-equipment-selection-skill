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

1. Extract known conditions, assumptions and TBD items. If the request is broad or under-specified, use guided requirement discovery before architecture decisions.
2. Identify mandatory requirements, availability/RTO/RPO targets, growth and budget constraints.
3. Decide the **minimum justified architecture** before selecting products.
4. Calculate CPU, memory, storage, historian, port and UPS requirements as applicable.
5. Define minimum and recommended technical specifications.
6. Research current product families and verify official specifications/lifecycle.
7. Apply Mandatory technical/compatibility constraints before preference scoring.
8. Normalize exact configurations and price evidence.
9. Compare cost, TCO where useful, reliability, lifecycle, operability and expansion capability among technically eligible alternatives.
10. Generate only the artifacts required by the user's project stage.
11. State risks, exclusions, upgrade triggers and vendor-confirmation items.

## Guided Requirement Discovery and Scenario Templates

When the user gives a broad project description, asks for an end-to-end recommendation, or omits requirements that could materially change architecture/product eligibility, load `references/decision-support.md`.

Structured discovery templates are in:

```text
assets/scenario-templates.json
```

Use `scripts/guide_requirements.py` when a concise deterministic checklist is useful:

```bash
python3 scripts/guide_requirements.py --list
python3 scripts/guide_requirements.py \
  --scenario manufacturing-scada-small \
  --input project-known-fields.json \
  --max-questions 7 \
  --pretty
```

Rules:

- Templates are **discovery aids, not predefined architectures**.
- User/project facts always override template suggestions.
- Suggested assumptions must remain visibly separate from known facts and TBD items.
- Do not silently turn a scenario template into HCI, HA, dual-core switching, firewall, Xinchuang, GPU or vendor requirements.
- Prefer a small set of high-value questions (normally 3–7) over a long questionnaire.
- Do not ask again for facts already supplied in the current request or accessible project materials.
- Missing minor details may be carried as explicit assumptions; missing Mandatory facts that change candidate eligibility must remain unresolved before final product recommendation.

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
scripts/calculate_tco.py
scripts/calculate_hci_failover.py
```

Sizing rules:

- Do not size a standalone physical application server from VM-count formulas.
- Estimate consolidated services separately: acquisition, runtime, database/historian, BI/reporting, Web and integration.
- Historian capacity uses historical points and effective sample rate, not total licensed tags.
- State RAID level, drive count, raw/usable capacity and independent backup separately.
- UPS sizing must check both W and VA and state the runtime objective; actual runtime must be validated against manufacturer runtime data.
- **Technical fit is a prerequisite for price comparison.** A cheaper SKU must not redefine the project requirement after pricing begins.

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

### Structured input contracts

For price evidence, server RFQs, TCO, HCI failover and real-project retrospectives, use the versioned Draft 2020-12 contracts under `schemas/`. Validate bundled or project inputs before calculation when Shell/Python is available:

```bash
python3 scripts/validate_json_schemas.py <input.json> --schema schemas/<name>.schema.json
```

Schema validation is a preflight contract, not a replacement for technical-fit, lifecycle, quotation or engineering checks. Reject unknown fields and invalid types instead of guessing their meaning.

Use `scripts/infra_cli.py list` to discover deterministic calculators and named contracts. Use
`scripts/infra_cli.py run <tool> -- <args>` only for deterministic calculation; do not treat the CLI
as a substitute for Agent research or selection judgment. For schema versions and migration load
`references/schema-governance.md`; for explicit private overlays load `references/private-extensions.md`.

### Real-project learning

When real project artifacts, quotations, awards, settlements or operational measurements are available, load `references/real-project-validation.md` and create an anonymized retrospective where useful.

- Keep `design-baseline-only`, quote, award, settlement and operational evidence stages distinct.
- Do not present a design budget revision as final procurement forecast accuracy.
- Record material error sources and convert transferable findings into workflow rules or regression tests.
- Remove customer, contact, supplier-sensitive, credential, network-address and location identifiers before publication.

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
- User-provided or project-saved current human quotations are valid evidence even when they have no public URL, provided channel, date, configuration match and commercial scope are captured.
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

### Mandatory technical-fit gate before price reduction

This gate applies to **every** downward price revision, including `fixed-sku` and commodity-like lines. Price research may identify candidates, but a cheaper candidate is eligible to influence the budget only after it is shown to satisfy the requirement that existed before price comparison.

Rules:

1. Preserve the required technical scope before researching cheaper candidates. Do not weaken CPU, memory, ports, display/OPS capability, UPS capacity/runtime, warranty, license scope or other mandatory attributes merely to match a cheaper listing.
2. Reject a cheaper SKU from the pricing anchor when its mandatory technical fit is unknown or fails. Keep its price only as excluded/context evidence.
3. For UPS lines, always load `references/ups-sizing.md` before lowering the budget. Establish protected load, W margin, VA margin, runtime objective and graceful-shutdown requirement first.
4. When a concrete UPS SKU is proposed as the reason for a lower budget and Shell/Python is available, run:

```bash
python3 scripts/calculate_ups.py <protected-load-W> \
  --runtime-minutes <minutes> \
  --candidate-w <candidate-output-W> \
  --candidate-va <candidate-VA> \
  --runtime-curve-verified \
  --shutdown-interface-verified
```

5. Use the UPS candidate as a lower-price anchor only when the result is `status = eligible-for-pricing`. If protected load/runtime is unresolved or the result is `not-eligible-for-pricing`, hold the previous UPS budget provisionally and mark it `Needs confirmation` rather than sizing the requirement from the cheap SKU.
6. A nominal `1500VA` label does not prove suitability; real output W, VA, runtime at actual load and required shutdown integration are independent checks.
7. Apply the same principle to displays and other bundled fixed SKUs: for example, a display without OS/network capability does not satisfy a browser/BI requirement unless OPS or an equivalent playback device is included in the compared commercial scope.

### Mandatory existing-budget revision workflow

Treat this as `budget-revision` mode. It is **mandatory** whenever the user asks to update, refresh, reprice, revise or optimize prices in an existing BOM, CSV, XLSX or budget file, even with only “更新一下价格”.

1. Read the source artifact first and preserve each existing line-item unit price as the **revision baseline**. A previous budget is not automatically current-price evidence, but it must not be silently overwritten by weaker evidence.
2. Before broad web research, inspect accessible project evidence for current quotations: the source file, adjacent/previous budget versions, quote records, notes, screenshots, user-provided figures and prior project artifacts. Do not discard a human quotation merely because it has no public URL.
3. Apply the **mandatory technical-fit gate before price reduction** to every line whose lower-priced candidate changes or leaves uncertain any mandatory requirement.
4. For every `configurable-enterprise` item, load `references/exact-configuration-pricing.md` and `references/live-price-research.md` before deciding a revised price.
5. If a proposed revision would **lower** an existing `configurable-enterprise` unit price, create structured price-evidence records and run the deterministic guard:

```bash
python3 scripts/normalize_price_evidence.py <evidence.json> \
  --summary \
  --strict-contract \
  --existing-budget <old-unit-price> \
  --product-class configurable-enterprise
```

6. Apply a lower price only when `budget_revision.decision` is `revise-to-current-anchor`. If the result is `hold-existing-provisional`, keep the old unit price, mark it `Needs confirmation`, and show weaker prices only as excluded/context evidence.
7. The following **cannot by themselves justify lowering** an existing configurable-enterprise budget: `Partial-config`, generic/model-family listings, market aggregators such as ZOL/PConline-style context pages, starting/base prices, historical transactions, component models, and engineering estimates.
8. One Tier-3 highly matched current quote is not enough by itself to lower an existing configurable-enterprise budget. Require at least one exact-current Tier-1/2 quote, or two independent Tier-3 highly matched current quotes.
9. Never derive a new lower “control price” by taking a partial public configuration and adding/subtracting an engineering adjustment. `Partial-config + configuration-difference estimate` is context only, not a downward budget anchor.
10. If strong current evidence is **higher** than the existing budget, revise upward or report the verified range; the guard is not a reason to preserve an obviously under-budgeted amount.
11. Recalculate line totals, contingency and project totals only **after** every relevant line passes the technical-fit gate and every configurable-enterprise line passes the price-evidence revision gate.
12. In the final response, explicitly list every configurable-enterprise line whose price changed, its old price, new price/range, evidence tier and revision decision. If none passed the gate, say that no such line was lowered.

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

### Mandatory server quotation workflow

For a server inquiry, freeze the exact technical and commercial RFQ baseline before collecting price. Load `references/server-quotation-workflow.md` and use:

```bash
python3 scripts/compare_server_quotes.py assets/server-rfq-example.json --pretty
```

A server quote can enter the budget anchor only when its technical-fit and commercial-completeness gates both pass. Require explicit CPU, memory, storage/RAID, NIC, redundant power, warranty, licenses, accessories, tax, freight, implementation, validity and orderability scope. Reject mixed currencies, expired quotes and duplicate evidence. Two independent exact-configuration quotes define the preferred control range; a partial web listing cannot lower the existing budget.

Treat independence as supplier independence, not quotation-number independence. Multiple quote IDs from the same supplier count as one source. Require a deterministic project `as_of_date`; a quote marked current is still excluded when its source date is older than the allowed freshness window (90 days by default). Risk reserve must be explicit, non-negative and no more than 100%.

## TCO Analysis

When multiple technically eligible alternatives differ materially in acquisition price, power, support, licenses, facility cost or implementation cost, load `references/tco.md` and use `scripts/calculate_tco.py`.

TCO rules:

- Mandatory technical/compliance fit comes before TCO.
- Use average IT power, not PSU nameplate wattage.
- Apply PUE once; do not double-count cooling electricity already represented by PUE.
- Use comparable tax, support, license and implementation scope across candidates.
- Report acquisition/CAPEX separately from 3-year/5-year TCO.
- Unknown material OPEX inputs remain TBD/Needs confirmation; do not silently make them zero in a procurement recommendation.
- TCO is a preference/cost dimension and cannot rescue a candidate that fails a Mandatory requirement.

Example:

```bash
python3 scripts/calculate_tco.py assets/tco-example.json --format markdown
```

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

Budget-summary wording rule:

- Do not claim the overall budget is `tax included`, `delivered`, `fully scoped` or equivalent unless those commercial attributes are confirmed for every material line relevant to the claim.
- If any material line still has unknown tax, warranty, implementation or delivery scope, state that the project total is based on currently available evidence and explicitly identify the remaining commercial-scope confirmations.

## Optional Artifact Modes

Load these only when requested or directly useful.

### vendor-compare

Use `references/decision-support.md`, `references/vendor-comparison.md` and optionally `scripts/compare_vendors.py`.

- Compare project-specific configurations, not brand reputation.
- Apply Mandatory constraints/knockout gates **before** weighted preference scoring.
- A missing Mandatory attribute is `CONDITIONAL`, not a silent PASS.
- PASS candidates always outrank CONDITIONAL candidates regardless of preference score.
- FAIL candidates are excluded; Mandatory failures cannot be rescued by a score.
- Typical scoring dimensions include TCO, lifecycle, operability, expansion, implementation complexity and evidence quality.

### tco-analysis

Use `references/tco.md` and `scripts/calculate_tco.py` when lifecycle operating costs materially change the comparison.

- Prefer 3-year and 5-year views.
- Keep CAPEX and OPEX visible separately.
- Do not use TCO as a substitute for current-price research.

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

## Principles

- Requirements first, products second.
- Architecture follows requirements.
- Scenario templates guide discovery; they do not define the architecture.
- Prefer the simplest architecture that satisfies mandatory requirements with acceptable risk.
- Do not reverse-engineer requirements from a favorite product.
- Separate verified specifications from assumptions and estimates.
- Separate technical evidence from price evidence.
- Mandatory constraints are evaluated before weighted preference scoring.
- PASS candidates outrank CONDITIONAL candidates; FAIL candidates are excluded.
- TCO compares technically eligible alternatives and never overrides Mandatory requirements.
- Compare exact configurations, not chassis/model family names.
- Price evidence is selected by configuration match, product class and evidence tier, not by naïvely averaging all observed prices.
- Current-price requests use live research when available.
- Technical fit must be validated before a cheaper candidate can influence a budget.
- Existing-budget downward revisions for configurable enterprise equipment must pass the deterministic price-evidence guard before the old price is changed.
- Keep tender parameters vendor-neutral unless a restriction is justified.
- Do not invent topology, licensing or safety details.
- Surface single points of failure, exclusions, uncertainty and upgrade triggers.

## Full Project Output

For a project-level design, normally include only the relevant sections from:

1. Known conditions / assumptions / TBDs
2. Guided requirement gaps/questions when material
3. Architecture decisions and rationale
4. Capacity calculations and assumptions
5. Recommended hardware/software configurations
6. SCADA/OT licensing and control requirements where applicable
7. Candidate products, Mandatory gate results and evidence
8. Vendor comparison and recommendation order when requested
9. TCO comparison when useful
10. Logical topology when useful
11. BOM and budget range
12. Compressible/optional items
13. Risks, exclusions, acceptance and confirmation items
14. An anonymized real-project retrospective when field evidence is available and publication is appropriate

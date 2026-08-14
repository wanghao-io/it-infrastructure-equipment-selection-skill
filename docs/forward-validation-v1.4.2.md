# v1.4.2 Independent Simulated Forward Validation

Date: 2026-08-15

## Scope and evidence boundary

This evaluation checks whether a fresh Agent can follow the Skill on realistic project prompts after the v1.4.2 usability and release-convergence changes.

- Four independent subagents received only the repository `SKILL.md` path and a user-style prompt.
- They did not receive the audit findings, intended fixes, expected answer or scoring conclusions.
- They could use bundled references and deterministic scripts, but could not modify the repository or a user project.
- No customer, supplier, quotation original, production system or `DS_OUTPUT` directory was used.

This is **simulated forward validation**, not proof of external-user adoption, current market-price accuracy, procurement outcome, settlement accuracy or operational reliability.

## Blocking criteria

A scenario fails if the answer does any of the following:

1. introduces HCI, HA, dual core, redundant firewalls or another prestige architecture without a requirement;
2. converts unknown Mandatory facts into PASS or a fabricated exact quantity;
3. uses licensed SCADA tags as historian points without evidence;
4. permits remote control to bypass PLC/equipment permissives or safety logic;
5. lowers an existing configurable-enterprise budget from starting-price, generic or historical evidence alone;
6. lets scoring or TCO rescue a Mandatory technical failure;
7. presents unresearched model, lifecycle or price information as current fact.

The review also checks route selection, fact/assumption/TBD separation, appropriate deterministic-tool use, risk disclosure and whether the next action is executable.

## Results

| Scenario | Main routes exercised | Result | Evidence from the answer | Improvement observation |
|---|---|---|---|---|
| 35-person office, ERP, files and a CNY 120k ceiling | guided requirements, architecture, server/storage/network/UPS, firewall, BOM | PASS | Rejected unjustified three-node HCI, dual core and dual firewalls; calculated only the known 40-port lower bound plus reserve; kept RTO/RPO, capacity, AP count, UPS and current price unresolved | The complete answer is useful but long; a decision-summary layer should precede the unchanged engineering detail |
| Two-line SCADA with mobile compressor start | SCADA/historian, UPS, OT control safety, architecture | PASS | Kept licensed 3,000 tags separate from historian points; treated UPS W/VA as a provisional target pending runtime curve and shutdown-interface evidence; kept PLC interlocks authoritative and supplied FAT/SAT cases | Temporary engineering assumptions were labeled, but their provenance could be more compactly summarized in one assumption ledger |
| Existing CNY 92k dual-socket server budget challenged at CNY 50k | budget revision, exact configuration, price evidence, server RFQ | PASS | Returned `hold-existing-provisional`; excluded a CNY 47k starting price and an unmatched historical transaction from the downward anchor; produced an exact-scope multi-supplier RFQ plan | The Agent used direct specialist scripts/references because guarded procurement commands are not yet first-class CLI subcommands |
| Three-node HCI N+1 plus incomplete TCO | HCI failover, TCO, Mandatory vendor comparison | PASS | Calculated CPU, memory and usable-storage failures after one node loss; refused to choose either candidate; kept candidate A's five-year TCO incomplete because support cost was TBD | A dedicated combined validation recipe could make the boundary between technical FAIL and incomplete TCO easier for occasional CLI users |

No blocking criterion was triggered in the four completed scenarios.

## What v1.4.2 demonstrates

- The shorter Router still reaches the detailed requirements, architecture, sizing, procurement, OT and delivery rules.
- Progressive disclosure did not remove the core safety behavior.
- Missing data remained visible instead of being converted into precise models, quantities or prices.
- Deterministic calculations remained subordinate to Mandatory engineering gates.
- The most consistent remaining friction is discovering the correct guarded command and controlling answer length, not a missing selection rule.

## v1.5 decision

v1.5 should be an evidence-gated usability release, not a product-database or feature-accumulation release.

### Proposed v1.5 scope

1. Add dedicated fail-closed CLI subcommands for the capabilities already classified as `public-gated`:
   - `guide` for discovery only, never architecture selection;
   - `server-quotes validate|compare`, always preflighted with the server RFQ contract;
   - `price-evidence`, always strict and versioned, without a legacy-input bypass;
   - `migrate`, preserving the source and refusing destination overwrite.
2. Add an optional decision-summary presentation layer:
   - conclusion and blocking facts first;
   - decisions that can be frozen now versus decisions awaiting evidence;
   - the 3–7 highest-value confirmations;
   - full calculations, evidence and acceptance detail retained in routed appendices rather than removed.
3. Turn this forward-validation method into a repeatable evaluation set with raw prompts, blocking criteria and sanitized outputs. Expand it before v1.5 to at least ten independent scenarios covering IT, OT, procurement and platform degradation.
4. Collect at least two non-maintainer external-user or artifact reviews before claiming v1.5 usability improvement. Keep design, quotation, award, settlement and operational evidence stages distinct.
5. After the new release workflow has completed successfully in normal use, evaluate protected `v*` tags and GitHub Immutable Releases as governance hardening.

### Explicitly deferred

- permanent vendor/model rankings;
- a public product or price database;
- automatic price crawling or purchasing;
- automatic discovery of private files or supplier data;
- a broad HTTP API;
- additional calculators without a demonstrated repeated project need;
- a new unified project-input Schema until external use shows that free-form discovery plus the existing focused contracts is insufficient.

### v1.5 release gate

Do not publish v1.5 until all of the following are true:

- all current deterministic, schema, router, installer and cross-platform tests remain green;
- every new guarded CLI command is fail-closed and has no silent legacy or overwrite path;
- at least ten independent forward scenarios contain no blocking violation;
- at least two non-maintainer reviews are recorded with their true evidence stage;
- no field result is described as price, settlement or operational validation without the corresponding evidence.

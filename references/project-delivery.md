# Project Delivery Consistency

Use when producing multiple representations of one project or revising quantities, phases, licenses or links.
Use `assets/project-delivery-example.json` and `schemas/project-delivery.schema.json`.
Run `python3 scripts/infra_cli.py project-check project-delivery delivery.json`.

## Record semantics

- `assets` are stable physical asset or homogeneous group IDs, not drawing-cell IDs.
- `quantity` is group quantity; `endpoint_ports` is the TOTAL occupied network ports of that group, not ports per machine.
- `power_w` is per unit at the documented design maximum. Quantity and power must use the same grouping.
- Keep `buy / existing / optional / future` and phase IDs explicit; final capacity is not phase-one purchase quantity.
- BOM asset rows partition an asset quantity; accessory/license rows have null asset_id.
- `representations` contain complete normalized projections of this record's asset scope from BOM/RFQ/diagram/text. For a partial drawing, use a separate scoped record, not silently omitted assets.
- The helper checks projections supplied by the caller; it does not automatically extract Word, Excel or source Draw.io content. Compare actual exports when creating projections.
- Link materials and per-asset dependencies are explicit requirements with evidence. Declare each requirement once.
- Do not hardcode two optics for every link: DAC/AOC and integrated ports differ.
- Do not hardcode one license per HA appliance: use the supplier's confirmed licensing model.
- Capacity evidence must state whether it is normal-state or single-survivor capacity.

## Checks

Compare model, quantity, phase and optional status across representations.
Aggregate all link-material and license dependencies before checking BOM quantities.
PoE demand is sum(quantity × maximum watts) × (1 + explicit reserve).
Controller-license demand is the selected asset count with the explicit reserve policy.
Validate current and final expansion scenarios separately; a current-phase PASS cannot prove future capacity.

Any unknown quantity/model/capacity/evidence remains visible. Missing or inconsistent asset coverage fails consistency.
A source diagram update invalidates old rendered/embedded images until regenerated against the same baseline.
A consistency PASS is neither technical eligibility nor procurement readiness.

## Cable inputs

For optional link.length fields, load `references/cabling-estimation.md`.
Never infer a communication protocol from conductor count. The instrument-to-gateway circuit and gateway Ethernet uplink are separate links and counting pools.

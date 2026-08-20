# Existing-Budget Revision Workflow

Use this workflow whenever the user asks to update, refresh, reprice, revise, optimize or compress prices in an existing BOM, CSV, XLSX or budget file. A short request such as “更新一下价格” still activates `budget-revision` mode.

This reference contains the mandatory decision rules. Use `references/live-price-research.md` for current-price collection, `references/price-evidence.md` for the structured evidence contract, `references/exact-configuration-pricing.md` for configurable enterprise equipment and `references/bom-checklist.md` before issuing the revised total.

## Non-negotiable outcome

- Preserve every existing line-item unit price as the **revision baseline** before research.
- A previous budget is not automatically current-price evidence, but it must not be silently overwritten by weaker evidence.
- A cheaper product may influence the budget only after explicit technical fit against the requirement that existed before pricing.
- Apply the technical-fit gate to `configurable-enterprise`, `fixed-sku` and `commodity-component` lines.
- A lower price is applied only when the deterministic result is `budget_revision.decision = revise-to-current-anchor`.
- If the result is `hold-existing-provisional`, retain the previous amount provisionally, mark it `Needs confirmation` and keep weaker prices only as excluded/context evidence.
- Strong current evidence above the previous amount may revise the budget upward; the guard must not preserve a known underestimate.

## Mandatory workflow

1. Read the source artifact first. Record line identity, quantity, old unit price, old total, configuration, commercial scope and currency without changing them.
2. Separate known facts, assumptions and unresolved fields. Missing technical requirements that change candidate eligibility remain TBD; they are not inferred from a cheaper listing.
3. Before broad market research, inspect accessible project evidence: the source file, adjacent or previous versions, saved quotation records, notes, screenshots and user-provided current figures. A traceable human quotation does not require a public URL.
4. Freeze the required technical and commercial scope for each line before comparing prices. Preserve CPU, memory, storage, ports, licenses, warranty, accessories, implementation, tax, delivery and other Mandatory attributes as applicable.
5. Classify each line as `configurable-enterprise`, `fixed-sku` or `commodity-component` and follow the matching live-research strategy.
6. Validate technical fit before price eligibility. Unknown or failed Mandatory fit excludes the price from the anchor and leaves it as context.
7. For current-price work, use live research when tools are available. If current evidence cannot be verified, return an engineering estimate or RFQ with `Needs confirmation`, not a remembered or stale price.
8. Normalize exact configuration, commercial scope, dates, currency, supplier/channel identity and decision scope using the versioned price-evidence contract.
9. For every proposed downward revision, run the deterministic budget-revision guard. Configurable enterprise equipment also requires the stronger evidence gate below.
10. Apply a revised price only after the result is `revise-to-current-anchor`. Do not manually reinterpret an excluded or provisional result.
11. Recalculate line totals, contingency and project totals only after every changed line passes its required gates.
12. Report every changed configurable-enterprise line with old price, new price/range, evidence tier and revision decision. If none passes, explicitly say that no configurable-enterprise line was lowered.

## Universal technical-fit gate

The technical-fit gate applies to every downward revision, not only servers.

- Preserve the original requirement before researching cheaper candidates.
- Require `technical_fit_status = PASS` and `eligible_for_pricing = true` before a price can become an anchor.
- A missing Mandatory attribute is unresolved, not a PASS.
- Do not weaken display/OPS capability, UPS capacity/runtime, port count, warranty, license scope or any other requirement to match a cheap SKU.
- Keep rejected candidates visible with an exclusion reason when they materially affect the market explanation.

For a UPS price reduction, load `references/ups-sizing.md` and establish protected load, W margin, VA margin, runtime objective and graceful-shutdown requirement. A concrete candidate may support a lower budget only when `scripts/calculate_ups.py` returns `status = eligible-for-pricing`. A nominal VA label alone is not evidence of W capacity or runtime.

For a display that must provide browser, BI or network playback, include OPS or an equivalent playback device in the technical and commercial scope unless the display itself provides the required capability.

## Configurable-enterprise downward gate

For servers, storage, HCI, configured firewalls, modular switches, project UPS and other `configurable-enterprise` equipment, a downward revision requires strong current evidence supporting the lower level:

- at least one Tier-1 or Tier-2 exact-current quotation; or
- at least two supplier-independent Tier-3 highly matched current quotations with the remaining differences explicitly normalized.

One Tier-3 quotation is not enough. Supplier independence is based on normalized supplier/channel identity, not quotation number. When one supplier has multiple eligible revisions, use the newest; for the same date prefer complete commercial scope and then the conservative higher comparable cost.

The following cannot by themselves justify lowering an existing configurable-enterprise budget:

- partial configuration;
- same-family or generic model listing;
- starting, base or bare-chassis price;
- market aggregator or price-history context;
- historical transaction;
- component-cost model;
- engineering estimate;
- `Partial-config + configuration-difference estimate`.

When only weak/context evidence exists, keep the old numeric amount only as a provisional carry-forward or use `TBD` when carry-forward would mislead the project stage. Do not label the old amount as a verified current price.

## Structured guard

Prefer the v2 price-evidence contract so all records belong to one explicit decision scope:

```json
{
  "schema_version": 2,
  "decision_scope_id": "project:bom-line-server-01",
  "items": []
}
```

Validate and assess the existing unit price:

```bash
python3 scripts/normalize_price_evidence.py evidence.json \
  --summary \
  --strict-contract \
  --existing-budget <old-unit-price> \
  --existing-currency <ISO-4217-code> \
  --product-class configurable-enterprise
```

Do not mix evidence from different BOM lines, products, product classes or projects into one range. The baseline currency is mandatory; do not compare or revise across currencies without an explicit dated conversion basis. A CLI product-class argument may confirm but never override a conflicting evidence class.

Interpret the result literally:

- `revise-to-current-anchor` — the proposed direction has sufficient eligible evidence; report the observed range and confidence.
- `keep-current-anchor` — the eligible anchor equals the existing amount/range.
- `hold-existing-provisional` — keep the old amount provisionally and disclose why confirmation remains necessary.
- `no-existing-budget` — this is a new budget, not a revision; use the normal price-anchor workflow.

## Match and evidence interpretation

Default server configuration-match guidance:

- `>= 0.95`: exact or effectively exact;
- `0.85–0.949`: highly comparable;
- `0.70–0.849`: partial comparison only;
- `< 0.70`: not a direct budget anchor.

System-derived evidence levels are:

- `Market-verified`;
- `Comparable-transaction`;
- `Estimated`;
- `Needs confirmation`.

A caller- or supplier-declared level is context only and cannot override the derived result. See `references/price-evidence.md` for v1/v2 field semantics and source priority.

## Required revision output

For every material line show, as applicable:

- item and exact configuration/SKU;
- product class and decision scope;
- old unit price and proposed/current range;
- technical-fit and price-eligibility result;
- source/channel and evidence date;
- configuration match and commercial-scope status;
- evidence tier, confidence and deterministic revision decision;
- excluded signals and their exclusion reasons;
- unresolved tax, warranty, implementation, delivery or orderability scope.

Only after line decisions are complete, update quantities, subtotals, contingency and total. Follow the commercial-claim boundary in `references/bom-checklist.md`: do not describe the whole budget as tax included, delivered or fully scoped unless every material line relevant to that statement is confirmed.

## Anti-patterns

Never:

- overwrite old prices before preserving the baseline;
- use a cheaper listing to redefine the requirement;
- discard a stronger current project quotation merely because it has no public URL;
- reconstruct an inaccessible quotation from memory;
- combine different decision scopes or count several quote IDs from one supplier as independent sources;
- average exact current quotations with weaker historical or generic prices;
- produce a compressed control price from a partial listing plus an engineering uplift;
- claim that a design-stage budget revision proves award, settlement or operational accuracy;
- hide unchanged provisional lines when no evidence passed the lowering gate.

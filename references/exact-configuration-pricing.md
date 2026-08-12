# Exact-Configuration Pricing

Use this reference for highly configurable enterprise equipment such as servers, storage, firewalls, HCI nodes, UPS systems and modular switches.

The pricing problem is not simply finding a price for the same model family. The goal is to find a price for a configuration that is commercially comparable to the required BOM.

## Core Rule

For pricing, **configuration match outranks source prestige**.

An exact current quotation from a manufacturer, official store/customer-service channel or authorized reseller is a stronger budget anchor than an older government award or a public listing for a materially different configuration.

A current quotation supplied by the user or preserved in the project workspace is also valid high-tier evidence when its seller/channel, date, exact configuration and commercial scope are captured. A public URL is not required for a human quotation to be stronger than a low-match web listing.

Technical specifications are different: official manufacturer documentation remains the preferred source for technical facts.

## Price Evidence Priority

Use the highest available tier and do not let lower tiers pull the budget away from it.

1. **Exact current formal quotation** — exact configuration, current date, tax/service scope known, from manufacturer/direct sales/official store/authorized reseller; this includes user-supplied or project-saved human quotations when the source details are recorded.
2. **Exact current market quotation** — exact configuration from a credible enterprise marketplace or comparable current sales channel.
3. **Highly matched current quotation** — current configuration with small, understood deviations.
4. **Comparable historical transaction** — government/public procurement transaction with sufficiently similar configuration and scope.
5. **Component-cost model** — estimated from current enterprise component/option costs when no exact quote exists.
6. **Generic model-family listing** — same chassis/model family but incomplete configuration.
7. **Engineering estimate** — no adequate current configuration-level evidence.

If Tier 1 evidence exists, Tier 4–7 evidence may be shown as context but must not replace or average down the Tier 1 budget anchor.

## Recover Existing Project Evidence First

When updating an existing BOM or project budget, do **not** start by discarding the project's existing quotation evidence and searching the public web from scratch.

Before external price research, inspect the information that is actually available in the current task, including:

- current user message and explicitly supplied quotation details;
- the input BOM/budget being updated;
- attached or referenced quote/evidence files;
- adjacent project files with clearly relevant names such as `quote`, `quotation`, `price-evidence`, `询价`, `报价` or equivalent, when the host has workspace search access.

Do not search unrelated personal directories. Only recover evidence from the project/task scope.

If a project contains a current exact-configuration quotation, preserve it as the primary evidence unless it is stale, invalidated, superseded or materially mismatched.

If a quotation existed only in another conversation/session and is not accessible in the current task, do not pretend to remember or reconstruct it. Ask the user to provide it again or recommend saving it into a project evidence file.

## Budget Revision Guardrail

This rule applies when the task is to **update, optimize, compress or revise an existing BOM budget**.

For `configurable-enterprise` equipment, a downward budget revision must be supported by strong current evidence.

A lower unit budget is allowed only when at least one of these is true:

- at least one Tier 1 or Tier 2 exact-current configuration quotation supports the lower level; or
- at least two independent Tier 3 highly matched current quotations support the lower level and the remaining configuration differences are explicitly normalized.

Tier 4–7 evidence **cannot by itself justify lowering an existing configured-enterprise budget**.

Therefore, do not:

- reduce a server budget from CNY 65,000 to CNY 60,000 because public same-family/partial configurations appear at CNY 16,000–47,000;
- create a new compressed control price from `partial public price + configuration-difference estimate`;
- treat `Estimated / Partial-config` as sufficient evidence for a downward budget optimization;
- use a low-match public listing to override a stronger project quotation that has no public URL.

When only Tier 4–7 evidence exists and the previous budget is numeric, retain the previous amount as a **provisional carry-forward**, mark it `Needs confirmation`, and state that it is not a verified current market price. If retaining the previous amount would be misleading for the project stage, use `TBD` instead of inventing a lower number.

Weak evidence may still trigger a warning that the existing budget could be high or low, but it must not silently change the configured-enterprise control price downward.

## Configuration Match Score

For a configurable server, use the following default weights unless the project has a better device-specific model:

| Field | Weight |
|---|---:|
| CPU model and quantity | 15% |
| Memory capacity/type/layout | 10% |
| SSD/NVMe configuration | 15% |
| HDD/capacity-tier configuration | 15% |
| RAID/HBA/cache/PLP | 15% |
| NIC / network ports | 5% |
| PSU quantity/wattage/redundancy | 5% |
| Warranty/support | 10% |
| Tax treatment | 5% |
| Mandatory accessories / rails / cables | 5% |

Each field may be scored from 0.0 to 1.0. The weighted total is the configuration-match score.

Interpretation:

- `>= 0.95` — exact or effectively exact configuration;
- `0.85–0.949` — highly comparable;
- `0.70–0.849` — partially comparable, use only with explicit adjustment;
- `< 0.70` — not a direct budget anchor.

A same-chassis listing does not receive an automatic high score.

## Current Quote Requirements

Capture, where applicable:

- exact model/chassis;
- CPU model and quantity;
- memory module count/capacity/type;
- SSD/NVMe/HDD quantity and capacity;
- RAID/HBA/controller/cache/PLP;
- NIC quantity/speed;
- PSU quantity/wattage;
- rails and mandatory accessories;
- operating-system or appliance licenses;
- subscription/security licenses;
- warranty/support term;
- implementation/service scope;
- tax/VAT status;
- shipping;
- quote date;
- seller/channel identity.

If these are not known, downgrade the configuration match and evidence confidence.

## Budget Output Rules

### Two or more exact current quotes

Use the observed quote range as the primary market range.

Example:

```text
Exact current quotes: CNY 89,000 and CNY 91,500 tax included
Recommended market range: CNY 89,000–91,500
Internal budget allowance: use the current quote range or a clearly stated procurement contingency
Evidence: Market-verified / Exact-config
```

Do not average in an older CNY 60,000 transaction for a different storage/RAID configuration.

### One exact current quote

Report the exact quote as the primary anchor and state that a second quote is recommended before fixing a procurement control price.

Do not invent a narrow range around one quotation unless a documented contingency rule is being applied.

### No exact current quote

Use the best available matched evidence and output a range, not a false-precision single number. For highly configurable enterprise equipment, mark the result `Estimated` or `Needs confirmation` until a configuration-level quote is obtained.

If this is an update to an existing BOM, also apply the **Budget Revision Guardrail** above: weak fallback evidence does not authorize a downward revision.

## Anti-Patterns

Do not:

- price a fully configured server from a bare-chassis listing;
- treat same model family as same configuration;
- average exact current quotes with low-match historical prices;
- use old government procurement as a live quote;
- prefer an official public listing with 40% configuration match over a current authorized quote with 98% match;
- hide tax, support, license, RAID, optics or accessory differences;
- output a precise single number when only weak evidence exists;
- lower an existing configurable-enterprise budget using only partial/generic public listings plus an engineering adjustment factor.

## Tooling

Use `scripts/normalize_price_evidence.py` to calculate normalized comparable cost, configuration-match score, evidence priority and preferred budget anchor when structured evidence is available.

When revising an existing budget, use its budget-revision assessment so weak evidence cannot silently justify a downward change.

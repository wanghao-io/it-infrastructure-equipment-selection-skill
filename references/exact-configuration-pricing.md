# Exact-Configuration Pricing

Use this reference for highly configurable enterprise equipment such as servers, storage, firewalls, HCI nodes, UPS systems and modular switches.

The pricing problem is not simply finding a price for the same model family. The goal is to find a price for a configuration that is commercially comparable to the required BOM.

## Core Rule

For pricing, **configuration match outranks source prestige**.

An exact current quotation from a manufacturer, official store/customer-service channel or authorized reseller is a stronger budget anchor than an older government award or a public listing for a materially different configuration.

Technical specifications are different: official manufacturer documentation remains the preferred source for technical facts.

## Price Evidence Priority

Use the highest available tier and do not let lower tiers pull the budget away from it.

1. **Exact current formal quotation** — exact configuration, current date, tax/service scope known, from manufacturer/direct sales/official store/authorized reseller.
2. **Exact current market quotation** — exact configuration from a credible enterprise marketplace or comparable current sales channel.
3. **Highly matched current quotation** — current configuration with small, understood deviations.
4. **Comparable historical transaction** — government/public procurement transaction with sufficiently similar configuration and scope.
5. **Component-cost model** — estimated from current enterprise component/option costs when no exact quote exists.
6. **Generic model-family listing** — same chassis/model family but incomplete configuration.
7. **Engineering estimate** — no adequate current configuration-level evidence.

If Tier 1 evidence exists, Tier 4–7 evidence may be shown as context but must not replace or average down the Tier 1 budget anchor.

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

## Anti-Patterns

Do not:

- price a fully configured server from a bare-chassis listing;
- treat same model family as same configuration;
- average exact current quotes with low-match historical prices;
- use old government procurement as a live quote;
- prefer an official public listing with 40% configuration match over a current authorized quote with 98% match;
- hide tax, support, license, RAID, optics or accessory differences;
- output a precise single number when only weak evidence exists.

## Tooling

Use `scripts/normalize_price_evidence.py` to calculate normalized comparable cost, configuration-match score, evidence priority and preferred budget anchor when structured evidence is available.

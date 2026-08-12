# Structured Price Evidence

Use this schema when equipment/budget research returns multiple prices. The goal is to decide whether two prices are commercially comparable before using them in a budget.

For highly configurable equipment also load `references/exact-configuration-pricing.md`. For current/live price research also load `references/live-price-research.md`.

## Core Rule

For **technical facts**, manufacturer documentation has the highest authority.

For **price anchoring**, configuration match and commercial scope come first. A current exact-configuration quote from a credible sales channel can be a stronger pricing anchor than an official public listing or historical procurement record for a materially different configuration.

Never average lower-quality evidence into an exact current quote range merely because more sources are available.

## Recommended JSON Record

```json
{
  "candidate": "model/configuration name",
  "product_class": "configurable-enterprise | fixed-sku | commodity-component",
  "configuration": "human-readable full configuration",
  "source_type": "manufacturer-direct-quote | official-store-human-quote | authorized-reseller-quote | enterprise-marketplace-exact-sku | market-aggregator | price-history | government-award | component-estimate | generic-listing | engineering-estimate",
  "quote_mode": "human-configured | exact-config | exact-sku | starting-price | base-config-listing | historical-transaction | estimate",
  "source": "source name or URL",
  "source_date": "YYYY-MM-DD",
  "quote_current": true,
  "orderability_confirmed": true,
  "price_scope_complete": true,
  "starting_price_or_base_config": false,
  "used_or_refurbished": false,
  "hardware_price": 0,
  "mandatory_accessories": 0,
  "required_licenses": 0,
  "warranty_support": 0,
  "required_implementation": 0,
  "tax_amount": 0,
  "shipping": 0,
  "currency": "CNY",
  "tax_included": true,
  "warranty": "3 years",
  "configuration_match": {
    "cpu": 1.0,
    "memory": 1.0,
    "ssd": 1.0,
    "hdd": 1.0,
    "raid": 1.0,
    "network": 1.0,
    "power": 1.0,
    "warranty": 1.0,
    "tax": 1.0,
    "accessories": 1.0
  },
  "comparable": true,
  "evidence_level": "Verified | Market-verified | Comparable-transaction | Estimated | Needs confirmation",
  "notes": ""
}
```

`configuration_match` values range from `0.0` to `1.0`. Omit a field only when it truly does not apply; an unknown field should not be silently treated as a full match.

`product_class` matters because a fully configured server should not use the same price-search strategy as a fixed switch SKU or an SSD.

`quote_mode` helps distinguish a human-confirmed configured quote from an e-commerce starting/base price that merely shares the same chassis name.

## Default Server Configuration Match Weights

| Field | Weight |
|---|---:|
| CPU model/quantity | 15% |
| Memory capacity/type/layout | 10% |
| SSD/NVMe configuration | 15% |
| HDD configuration | 15% |
| RAID/HBA/cache/PLP | 15% |
| NIC/network | 5% |
| PSU/redundancy | 5% |
| Warranty/support | 10% |
| Tax | 5% |
| Mandatory accessories | 5% |

Interpretation:

- `>= 0.95`: exact/effectively exact configuration;
- `0.85–0.949`: highly comparable;
- `0.70–0.849`: partial comparison only;
- `< 0.70`: not a direct budget anchor.

For another equipment class, change the weights when justified and document the change.

## Comparable Cost

Normalize to:

```text
hardware
+ mandatory accessories
+ required licenses
+ warranty/support
+ required implementation
+ tax
+ shipping
```

Use `scripts/normalize_price_evidence.py`.

## Price Evidence Priority

For budget anchoring, prefer:

1. exact current formal quote from manufacturer/direct/official/authorized channel;
2. exact current credible market quote;
3. highly matched current quote;
4. comparable historical government/public transaction;
5. component-cost model;
6. generic model-family listing / market aggregator / price-history context;
7. engineering estimate.

Lower-priority evidence can be shown as context, but must not override a higher-priority exact-current quote.

A market aggregator or price-history service may be useful for a fixed SKU or component, but it is not automatically a configured-enterprise quote.

## Comparability Gate

Before treating a price as directly comparable, confirm:

- same functional class;
- configuration-match score is sufficiently high;
- same included licenses;
- comparable warranty/support term;
- same tax treatment;
- mandatory accessories included;
- implementation scope understood;
- source date sufficiently current for the decision;
- price is not only a starting/base-configuration teaser;
- orderability is not explicitly known to be false;
- used/refurbished status is acceptable if applicable.

If one of these materially differs, keep the evidence but set `comparable: false` or record an `anchor_exclusion_reasons` condition and explain why.

## Interpretation

Prefer a smaller number of configuration-matched records over many unrelated prices.

Do not average:

- bare chassis and configured server;
- server with different CPU/memory/storage/RAID merely because the chassis is identical;
- switch without optics and switch with optics;
- appliance-only firewall and licensed/subscribed firewall;
- UPS main unit and UPS plus battery cabinets;
- exact current quotes and low-match historical transactions into one blended mean.

## Live Price Signal Rules

For current price research:

- live research is required when live search tools are available;
- classify each line as `configurable-enterprise`, `fixed-sku`, or `commodity-component` before selecting price sources;
- configured enterprise equipment should seek configuration-level quotations first;
- fixed SKUs/components may rely more heavily on multiple current marketplace listings;
- starting prices, unavailable configurations, incomplete commercial scope, and used/refurbished offers must be explicitly flagged;
- market aggregators, price-history tools, and deal communities are normally context sources unless the exact seller/SKU/quote has been independently verified.

## Budget Anchor Rules

- Two or more exact current quotes: use the observed exact-quote range as the primary market range.
- One exact current quote: use that quote as the primary anchor and request a second quote before fixing a procurement control price.
- No exact current quote: use the best matched evidence and output a range with `Estimated` or `Needs confirmation` as appropriate.
- Do not create false precision from weak evidence.

## Output

For important equipment show:

| Candidate | Product class | Exact configuration | Match score | Source type/date | Normalized cost | Priority | Anchor eligible? | Evidence level |
|---|---|---|---:|---|---:|---:|---|---|

Then report separately:

```text
Exact current quote range: CNY X–Y (if available)
Current market/context range: CNY P–Q
Historical comparable range: CNY A–B (context only)
Recommended project budget: CNY M–N
Evidence date: YYYY-MM-DD
Confidence: Market-verified / Estimated / Needs confirmation
```

Do not let historical, generic, starting-price or unavailable evidence mechanically pull an exact current quote range downward.

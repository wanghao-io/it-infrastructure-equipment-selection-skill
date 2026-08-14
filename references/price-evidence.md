# Structured Price Evidence

Use structured price evidence when equipment or budget research returns multiple price signals. The purpose is to decide which records are technically and commercially comparable before any price can influence a recommendation or budget.

For current research also load `references/live-price-research.md`. For configurable enterprise equipment load `references/exact-configuration-pricing.md`. For an existing budget load `references/budget-revision.md`.

## Contract choice

The unversioned schema path `schemas/price-evidence.schema.json` is the frozen v1 contract. Continue accepting valid v1 inputs while v1 remains supported.

Use `schemas/v2/price-evidence.schema.json` for new integrations and new structured evidence files. V2 adds:

- one explicit `decision_scope_id` for the whole evidence set;
- mandatory `technical_fit_status` and `eligible_for_pricing` on every record;
- caller declarations separated from system-derived evidence levels;
- fields required by current freshness, used-equipment and supplier-independence rules.

Read `references/schema-governance.md` before migration. `scripts/migrate_schema.py` is non-destructive and must not invent a decision scope, `PASS`, `Verified`, zero or a current date.

## Core rules

- Manufacturer documentation is normally strongest for technical facts.
- Configuration match, current orderability and complete commercial scope determine whether a price can anchor a budget.
- Every product class fails closed until technical fit is explicitly `PASS` and `eligible_for_pricing` is `true`.
- Do not aggregate evidence from different BOM lines, product families, alternatives or projects into one range.
- Quote numbers are records, not independent market sources; normalize supplier/channel identity before counting evidence.
- Never average lower-quality evidence into an exact-current quote range merely because more sources are available.
- Schema validation confirms structure, not truth, authorization, technical fit or evidence quality.

## Recommended v2 envelope

```json
{
  "schema_version": 2,
  "decision_scope_id": "project:bom-line-server-01",
  "items": [
    {
      "candidate": "Synthetic exact server quote",
      "product_class": "configurable-enterprise",
      "configuration": "Required project configuration with complete commercial scope",
      "source_type": "authorized-reseller-quote",
      "quote_mode": "human-configured",
      "source": "synthetic authorized supplier",
      "source_date": "2026-08-14",
      "as_of_date": "2026-08-14",
      "quote_current": true,
      "technical_fit_status": "PASS",
      "eligible_for_pricing": true,
      "orderability_confirmed": true,
      "price_scope_complete": true,
      "starting_price_or_base_config": false,
      "used_or_refurbished": false,
      "hardware_price": 100000,
      "mandatory_accessories": 0,
      "required_licenses": 0,
      "warranty_support": 0,
      "required_implementation": 0,
      "tax_amount": 0,
      "shipping": 0,
      "currency": "CNY",
      "tax_included": true,
      "warranty": "3 years",
      "exact_configuration_match": true,
      "comparable": true,
      "supplier": "Synthetic supplier",
      "sales_channel": "authorized",
      "quote_id": "Q-001",
      "quote_valid_until": "2026-09-14"
    }
  ]
}
```

Use one narrow decision scope, for example one BOM line or one normalized alternative. The scope identifier is not a customer name and should not contain confidential data.

Supplier files are raw facts, not decision records. A supplier must not decide `technical_fit_status`, `eligible_for_pricing`, `comparable`, `exact_configuration_match` or evidence level. Strip those fields during private ingestion and derive them only after independent requirement, engineering and commercial checks.

## Strict validation and normalization

Validate the versioned envelope before a pricing decision:

```bash
python3 scripts/normalize_price_evidence.py evidence.json \
  --summary \
  --strict-contract
```

Use `--legacy-input` only for an explicitly accepted unversioned legacy input; it emits a warning and performs no schema preflight. Do not silently treat legacy input as v2.

The normalizer:

- preserves a caller declaration as `declared_evidence_level` context;
- computes `derived_evidence_level`, `price_signal_role`, match score and exclusions;
- rejects mixed decision scopes and mixed anchor currencies;
- fails closed when technical fit or price eligibility is not explicit;
- deduplicates independent evidence by normalized supplier/channel or source identity;
- selects the newest eligible record from one supplier; for the same date it prefers complete commercial scope and then the conservative higher comparable cost;
- keeps excluded signals visible without averaging them into the preferred anchor.

The system-derived result controls the decision. A caller-declared `Verified` value cannot promote an ineligible record.

## Product classes

Classify each record before selecting price sources:

- `configurable-enterprise` — servers, storage, HCI, configured firewalls, modular switches, project UPS and other configuration-sensitive systems;
- `fixed-sku` — fixed switches, APs, displays, Mini PCs, NAS and fixed UPS SKUs;
- `commodity-component` — CPU, DIMM, SSD/HDD, optics, cables and other standard components.

The evidence strategy differs by class, but the technical-fit gate applies to all three.

## Comparable cost

Normalize the disclosed commercial scope to:

```text
hardware
+ mandatory accessories
+ required licenses
+ warranty/support
+ required implementation
+ tax
+ shipping
```

`TBD`, `Needs confirmation`, invalid or negative material costs do not become zero. They exclude an otherwise incomplete signal from the anchor where the missing scope matters.

## Configuration match

Default server weights are:

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

- `>= 0.95`: exact or effectively exact;
- `0.85–0.949`: highly comparable;
- `0.70–0.849`: partial comparison only;
- `< 0.70`: not a direct budget anchor.

For another equipment class, use justified device-specific attributes and document the weights. Unknown attributes are not full matches.

## Evidence priority

Use the strongest eligible tier without blending lower tiers into it:

1. exact current formal quote from manufacturer, direct, official or authorized channel;
2. exact current credible market quote;
3. highly matched current quote;
4. comparable historical government/public transaction;
5. component-cost model;
6. generic model-family listing, market aggregator or price-history context;
7. engineering estimate.

An exact current quotation may be stronger price evidence than an official public product page or historical transaction for a different configuration. A market aggregator or price-history service may help with a fixed SKU or component, but it does not automatically become a configured-enterprise quote.

## Comparability gate

Before setting `comparable: true`, confirm as applicable:

- same decision scope and functional class;
- sufficient configuration match;
- required licenses, accessories and implementation included or normalized;
- comparable warranty/support and tax treatment;
- explicit currency and current `as_of_date`;
- source date within the allowed freshness window;
- quote validity and current orderability;
- price is not a starting/base-configuration teaser;
- used/refurbished status is allowed when applicable;
- supplier/channel identity is sufficient for independence checks.

If a material condition is unknown or different, keep the record as context with `comparable: false` or an explicit anchor exclusion reason.

## Budget anchor interpretation

- Two or more supplier-independent exact-current quotes: use the observed exact-quote range as the primary current range.
- One exact-current quote: use it as the primary anchor with medium confidence and seek a second independent quote before fixing a procurement control price.
- No exact-current quote: use the strongest eligible matched evidence, report a range and use `Estimated` or `Needs confirmation` as appropriate.
- A government award is historical comparable evidence, not a live quote.
- Starting prices, unavailable offers and incomplete configurations remain context.
- Existing-budget reductions must also pass `references/budget-revision.md`.

Do not average:

- bare chassis and configured servers;
- materially different CPU, memory, storage or RAID configurations;
- switches without optics and switches with optics;
- appliance-only firewalls and licensed/subscribed firewalls;
- UPS main units and UPS systems that require battery cabinets;
- exact-current quotes and lower-match historical or generic evidence.

## Required output

For important equipment show:

| Candidate | Scope | Product class | Exact configuration | Technical fit | Match | Source/date | Comparable cost | Priority | Anchor eligible | Derived level |
|---|---|---|---|---|---:|---|---:|---:|---|---|

Then report separately:

```text
Exact current quote range: CNY X–Y
Current market/context range: CNY P–Q
Historical comparable range: CNY A–B (context only)
Recommended project budget: CNY M–N
Evidence as of: YYYY-MM-DD
Confidence: Market-verified / Comparable-transaction / Estimated / Needs confirmation
Excluded signals: source and reason
```

Never let caller declarations, duplicate quotation numbers, stale evidence, different decision scopes or misleading low-price signals mechanically lower the preferred budget anchor.

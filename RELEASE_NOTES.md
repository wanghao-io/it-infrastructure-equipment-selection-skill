# IT Infrastructure Equipment Selection Skill v1.1.1

## Exact-Configuration & Live Pricing Fix

v1.1.1 is a pricing-accuracy release. It fixes a major weakness in enterprise hardware budgeting: treating prices for the same chassis or model family as if they represented the same procurement configuration.

The guiding rule is:

> **Technical facts follow authoritative manufacturer documentation. Price anchors follow configuration match, current orderability and complete commercial scope.**

## What's Fixed

- Current exact-configuration quotations now outrank lower-match historical or generic model-family prices when setting budget anchors.
- Two or more exact current quotes define the primary observed market range without being averaged together with weaker evidence tiers.
- One exact current quote is used as the primary anchor while explicitly recommending a second quote before fixing a procurement control price.
- Same-chassis listings are no longer treated as equivalent procurement configurations.
- Bare-chassis prices, starting/base prices, unavailable offers, low-match configurations and incomplete commercial scope are excluded from the primary budget anchor.
- Highly configurable enterprise equipment without exact current quotations now returns a range with `Estimated` or `Needs confirmation` instead of false precision.
- Current-price requests require live research when live research tools are available.

## Live Price Research

A new workflow classifies the procurement object before selecting price channels:

- `configurable-enterprise` — servers, storage, HCI, configured firewalls, modular switches and project UPS systems;
- `fixed-sku` — fixed switches, APs, displays, Mini PCs, NAS and fixed UPS SKUs;
- `commodity-component` — CPUs, DIMMs, SSDs/HDDs, optics, cables and standard accessories.

This prevents applying commodity-product shopping logic to highly configurable enterprise systems.

For China-market research, manufacturer/direct/official/authorized quotations, JD/Tmall official or enterprise channels, ZOL/market aggregators, price-history tools and government-procurement records are used according to the equipment class and evidence role rather than through one universal website ranking.

## Configuration Match Scoring

The default server match model evaluates:

- CPU model and quantity
- memory capacity/type/layout
- SSD/NVMe configuration
- HDD configuration
- RAID/HBA/cache/PLP
- NIC/network ports
- PSU/redundancy
- warranty/support
- tax treatment
- mandatory accessories

Default interpretation:

```text
>= 0.95      Exact / effectively exact
0.85–0.949   Highly comparable
0.70–0.849   Partial comparison only
< 0.70       Not a direct budget anchor
```

## Price Evidence Priority

1. Exact current formal quotation
2. Exact current credible market quotation
3. Highly matched current quotation
4. Comparable historical transaction
5. Component-cost model
6. Generic model-family listing
7. Engineering estimate

Lower-priority evidence remains useful as context but does not mechanically pull a stronger exact-current quote range upward or downward.

## Tooling

`normalize_price_evidence.py` now supports configuration-match scoring and preferred budget-anchor selection:

```bash
python scripts/normalize_price_evidence.py assets/price-evidence-example.json --summary
```

Outputs include fields such as:

- `configuration_match_score`
- `evidence_priority`
- `anchor_eligible`
- `anchor_exclusion_reasons`
- `price_signal_role`
- `confidence_level`
- preferred budget low/high

## Regression Validation

Regression tests now explicitly verify that two current exact server quotations remain the budget anchor even when cheaper historical, aggregator, bare-chassis or starting-price signals are present.

GitHub Actions validates the pricing regression path together with the existing architecture, sizing, vendor-comparison, tender-specification and topology-generation tests.

## Upgrade Notes

No migration is required from v1.1.0. Existing users can update the skill directory and immediately use the new price-research and evidence-ranking rules.

## License

MIT License

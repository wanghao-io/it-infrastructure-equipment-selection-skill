# Infrastructure TCO Model

Use TCO when two or more technically eligible alternatives differ materially in power, support, license, facility or implementation cost.

Do not use TCO to rescue a candidate that fails a Mandatory requirement.

## Scope

The bundled calculator intentionally stays simple and auditable:

```text
CAPEX
= purchase cost
+ one-time implementation

Energy cost
= average IT power (kW)
× PUE
× operating hours
× electricity rate

Recurring OPEX
= annual support
+ annual licenses/subscriptions
+ annual facility/rack cost not already represented by PUE
+ other explicit annual OPEX

TCO
= CAPEX
+ energy cost over horizon
+ recurring OPEX over horizon
```

Default comparison horizons are 3 and 5 years.

## Input rules

Use **average IT input power**, not PSU nameplate capacity.

For example, a server with two 800 W PSUs does not mean its average load is 1600 W.

PUE represents facility overhead around IT electricity. If PUE is used, do not separately add the same cooling electricity again.

Use comparable commercial scope across all candidates:

- same tax treatment;
- same support horizon;
- same required licenses;
- same implementation scope;
- same rack/facility cost convention.

If a cost is unknown, keep it explicit as TBD/Needs confirmation rather than quietly assuming zero in a procurement recommendation.

## JSON example

See:

```text
assets/tco-example.json
```

Run:

```bash
python scripts/calculate_tco.py assets/tco-example.json --format markdown
```

or:

```bash
python scripts/calculate_tco.py assets/tco-example.json --pretty
```

## Interpretation

Report both:

- acquisition/CAPEX;
- 3-year and/or 5-year total TCO.

A lower acquisition price may have higher TCO, but TCO is only one decision dimension.

Recommended decision order:

```text
Mandatory technical/compliance fit
        ↓
lifecycle / orderability / supportability
        ↓
TCO and preference scoring
        ↓
current price evidence and procurement decision
```

When electricity rate, PUE, average load or annual support/license costs are estimates, label the TCO accordingly.

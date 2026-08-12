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

When electricity cost is included, provide PUE explicitly. The calculator does not silently assume `PUE = 1.0` for a cost-bearing comparison.

Use comparable commercial scope across all candidates:

- same tax treatment;
- same support horizon;
- same required licenses;
- same implementation scope;
- same rack/facility cost convention.

If a cost is unknown, keep it explicit as TBD/Needs confirmation rather than quietly assuming zero in a procurement recommendation.

The calculator distinguishes an explicit numeric `0` from a missing value. For procurement-grade TCO, explicitly provide these fields for every candidate, using `0` only when that cost is intentionally excluded or known to be zero:

```text
purchase_cost
one_time_implementation
average_it_power_w        # required when electricity cost is included
annual_support
annual_license
annual_facility
annual_other_opex
```

If one or more required inputs are missing, the result is:

```text
status = incomplete-needs-confirmation
total_tco = TBD
known_cost_floor = <sum of only the explicit known inputs>
```

An incomplete row must not be ranked against a complete row by `total_tco`. The known-cost floor is diagnostic context only, not a final TCO.

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

# UPS Sizing Reference

Use `scripts/calculate_ups.py` for a transparent project-level W/VA estimate and, when comparing a concrete SKU, for a deterministic technical-fit gate before pricing.

## Core Rule: Specification Before Price

**Do not let a cheaper UPS redefine the project requirement.**

The required protected load, margin, runtime objective and shutdown behavior must be established before a lower-priced UPS SKU is accepted into the budget.

A nominal label such as `1500VA` is not enough. The candidate must satisfy both its real output rating in W and its VA rating, and any required runtime/shutdown integration must be verified.

If the protected load or runtime objective is unknown during an existing-budget revision, do not lower the previous UPS budget merely because a cheaper retail SKU exists. Keep the prior amount provisionally and mark the line `Needs confirmation` until technical fit can be checked.

## 1. Define the Objective First

Common objectives differ:

- protect against brief outages and allow graceful server shutdown;
- improve power quality;
- maintain service for a defined runtime;
- support high-availability or critical operations.

Do not select an online long-runtime UPS when the actual requirement is only several minutes of ride-through and automated shutdown.

## 2. Protected Load

Count only the equipment the UPS is intended to protect, for example:

```text
server + switch + backup appliance + required management equipment
```

Do not automatically include operator PCs or large screens if they do not need backup power.

Prefer measured or manufacturer-backed load data. If only an engineering estimate is available, state the assumption and retain suitable margin.

## 3. Calculate Both W and VA

Use:

```text
required_W = protected_load_W × capacity_margin
required_VA = required_W / power_factor
```

Then select a UPS whose **W rating and VA rating** both satisfy the requirement.

A 20–30% project margin can be a starting assumption; actual load growth or vendor guidance overrides it.

Example deterministic sizing:

```bash
python3 scripts/calculate_ups.py 800 --runtime-minutes 10
```

## 4. Candidate Gate Before Pricing

When a candidate UPS SKU is being used to justify a budget change, validate it before comparing price:

```bash
python3 scripts/calculate_ups.py 800 \
  --runtime-minutes 10 \
  --candidate-w 1500 \
  --candidate-va 2000 \
  --runtime-curve-verified \
  --shutdown-interface-verified
```

Only a result with:

```text
status = eligible-for-pricing
```

may be used as a technically valid lower-price candidate.

A result of `not-eligible-for-pricing` means the price is irrelevant to the current requirement until the failed technical checks are resolved.

Typical rejection reasons include:

- candidate real-output W below the required margin;
- candidate VA below the required margin;
- runtime curve not verified at the protected load;
- graceful-shutdown interface/software not verified when required.

This gate is especially important during budget optimization: a `1500VA/900W` product must not be treated as equivalent to a larger UPS simply because its VA number looks sufficient.

## 5. Runtime

State the runtime objective explicitly, such as:

- 5 minutes;
- 10 minutes;
- 15 minutes;
- long-duration runtime.

Do not calculate actual runtime only from nominal battery Wh. Battery voltage, discharge rate, efficiency, age and UPS design affect runtime.

Validate the selected model against the manufacturer's runtime curve at the actual protected load.

## 6. Graceful Shutdown

For a single production server whose goal is safe shutdown, confirm:

- USB/serial/network management interface;
- supported shutdown software/agent;
- OS compatibility;
- shutdown delay;
- database/SCADA service-stop behavior;
- automatic restart/recovery expectation after power returns.

## 7. UPS Type

### Line-interactive / economical UPS

Can be appropriate for:

- short ride-through;
- graceful shutdown;
- moderate protected IT load;
- acceptable site power quality.

Verify waveform and server PSU compatibility.

### Online double-conversion UPS

Evaluate when required by:

- power-quality conditions;
- strict continuity requirements;
- longer runtime architecture;
- project/customer standard.

Do not assume online UPS is always required for every server room.

## 8. BOM Items

Check:

- UPS main unit;
- battery pack/cabinet if required;
- rack kit;
- communication/network card;
- PDU/output sockets;
- shutdown integration;
- warranty/battery warranty;
- replacement battery lifecycle.

## 9. Budget Wording

Do not describe the overall BOM as `tax included`, `delivered`, `fully scoped` or equivalent unless those commercial attributes are confirmed for every material line that affects the statement.

When some lines still have unknown tax, warranty, implementation or delivery scope, prefer wording such as:

```text
Estimated from current available evidence; tax, warranty, implementation and/or delivery scope remains to be confirmed for identified lines.
```

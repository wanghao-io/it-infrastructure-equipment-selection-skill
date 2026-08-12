# UPS Sizing Reference

Use `scripts/calculate_ups.py` for a transparent project-level W/VA estimate.

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

## 3. Calculate Both W and VA

Use:

```text
required_W = protected_load_W × capacity_margin
required_VA = required_W / power_factor
```

Then select a UPS whose **W rating and VA rating** both satisfy the requirement.

A 20–30% project margin can be a starting assumption; actual load growth or vendor guidance overrides it.

## 4. Runtime

State the runtime objective explicitly, such as:

- 5 minutes;
- 10 minutes;
- 15 minutes;
- long-duration runtime.

Do not calculate actual runtime only from nominal battery Wh. Battery voltage, discharge rate, efficiency, age and UPS design affect runtime.

Validate the selected model against the manufacturer's runtime curve at the actual protected load.

## 5. Graceful Shutdown

For a single production server whose goal is safe shutdown, confirm:

- USB/serial/network management interface;
- supported shutdown software/agent;
- OS compatibility;
- shutdown delay;
- database/SCADA service-stop behavior;
- automatic restart/recovery expectation after power returns.

## 6. UPS Type

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

## 7. BOM Items

Check:

- UPS main unit;
- battery pack/cabinet if required;
- rack kit;
- communication/network card;
- PDU/output sockets;
- shutdown integration;
- warranty/battery warranty;
- replacement battery lifecycle.

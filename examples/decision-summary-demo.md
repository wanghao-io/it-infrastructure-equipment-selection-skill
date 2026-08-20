# Synthetic Decision-Summary Demo

This example demonstrates output shape only. Names and costs are synthetic and are not current market evidence.

## User input

> Size a small manufacturing SCADA site with 2,000 historical points, 30 PLCs, ten-minute UPS shutdown support and an initial budget. Avoid unnecessary HCI. Current quotations are not available.

## Routed decision

- Modes: `project-design + server-sizing + scada-sizing + ups-sizing + bom-budget`.
- Not triggered: HCI, current-price anchor, domestic/Xinchuang and remote physical control.
- Capability fallback: without live quotations, prices remain `Needs confirmation` and the existing budget is not lowered.

## One-page decision summary

### Current conclusion

Use the minimum supportable standalone or simple virtualized architecture after application-vendor sizing. HCI is not justified by the supplied requirements. Final server count remains `CONDITIONAL` until RTO/RPO and maintenance-window facts are confirmed.

### Can be frozen now

- Historian sizing must use actual historical points and effective sampling classes.
- UPS must pass both W and VA and be verified against a ten-minute manufacturer runtime curve.
- RAID is not backup; independent backup scope is Mandatory.

### Mandatory blockers

- SCADA/driver support matrix and exact software versions;
- RTO/RPO and acceptable single-server outage;
- per-class sampling intervals and retention;
- protected load, power factor, shutdown interface and runtime curve;
- exact server configuration and current commercial quotations.

### Highest-value confirmations

1. Does loss of one server stop production, and for how long is that acceptable?
2. Which points are recorded at 1 s, 10 s and event-driven rates?
3. Which SCADA, database, OS and PLC-driver versions are Mandatory?
4. What measured W/VA load must the UPS protect?
5. Is the budget tax included, delivered and inclusive of licenses/support?

### Assumption/evidence ledger

| Item | State | Effect |
|---|---|---|
| 2,000 historical points | Fact supplied | Capacity input |
| sampling profile | TBD | Historian capacity unresolved |
| HCI requirement | Not supplied | Do not introduce HCI |
| current price evidence | Unavailable | Keep budget provisional |

## Detailed artifacts

The full answer would append calculation outputs, the exact-config RFQ, provisional BOM, acceptance checks, risks and upgrade triggers. The summary never replaces those artifacts.

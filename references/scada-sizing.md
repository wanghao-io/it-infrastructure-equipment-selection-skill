# SCADA Sizing and Licensing Reference

Use this reference for SCADA, historian, data-acquisition, operator-client, web-dashboard and reporting projects.

## 1. Separate Point Classes

Do not treat every project variable as the same kind of licensed or historical point.

Classify at least:

- physical I/O / PLC tags;
- calculated/internal tags;
- alarm-only tags;
- control command tags;
- historical tags;
- fast-sampled tags;
- slow utility/energy tags;
- diagnostic/device-health tags.

The tender or vendor must define what counts toward licensed I/O points.

## 2. Point Count

Start with the engineering point list, then add controlled headroom.

Recommended output:

```text
Current required external I/O points
+ confirmed phase-1 additions
+ expansion reserve
= licensed point target
```

Do not buy a larger license only because “more is safer.” Compare the next available license tier against expected growth.

If a vendor offers fixed tiers such as 1500 / 3000 / 5000 tags, show which tier is technically required and which points can be excluded without losing useful monitoring, alarms or controls.

## 3. Scan and Historian Strategy

Do not assume every point is stored every second.

Typical engineering classes may include:

- fast process / control feedback: 0.5–2 s where justified;
- normal equipment state: 2–5 s;
- temperature/pressure/utility: 5–30 s depending on dynamics;
- counters/energy/environmental values: 10–60 s where acceptable;
- event/alarm data: event-driven where supported.

These are starting ranges, not mandatory rules. Process requirements and vendor guidance override them.

Prefer deadband, exception reporting or historian compression where supported.

## 4. Historian Capacity

Estimate data volume from **historical points**, not total licensed points.

Approximate uncompressed record count:

```text
records_per_day = historical_points × 86400 / effective_sample_seconds
```

Approximate storage:

```text
GB_per_day = records_per_day × bytes_per_record / 1e9 × compression_factor
```

Where `compression_factor` is the fraction retained after effective compression, for example 0.25 means about 25% of the raw estimate. Do not claim a compression ratio unless validated by the historian/vendor or measured workload.

Capacity planning must include:

- retention period;
- database/index overhead;
- temporary/import space;
- growth reserve;
- free-space reserve;
- backup copies outside the online historian.

Use `scripts/calculate_historian.py` for transparent estimates.

## 5. Server Workload Components

For a consolidated SCADA server, estimate each service separately:

- acquisition/communication service;
- SCADA runtime;
- historian/database;
- alarm/event service;
- web publishing;
- BI/reporting;
- integration/API/OPC services;
- OS/management overhead.

Do not size a physical server only from VM count when the system is not a virtualization cluster.

Use `scripts/calculate_server_capacity.py` with service components and explicit headroom.

## 6. Storage Layout

Prefer workload separation where budget allows:

- OS/application: mirrored SSD (RAID1);
- current database / hot data: enterprise SSD, commonly RAID1 or RAID10 depending on write load;
- historical archive: HDD or SSD array selected from retention/performance needs, commonly RAID10/RAID6 depending on risk and usable capacity tradeoff;
- backup: independent target, not another directory on the same RAID set.

RAID is availability against drive failure, not backup.

## 7. SCADA Licensing Breakdown

Never write only “SCADA software — 1 set” when preparing procurement documents.

Request separate commercial confirmation for:

1. Runtime / production server license;
2. Development / engineering license;
3. external I/O point license and available tiers;
4. operator/client licenses and whether they are concurrent or named;
5. Web publishing / browser client licenses and concurrent-user limits;
6. historian / historical trend capability;
7. alarm/event management;
8. reporting/API/ODBC/SDK interfaces;
9. communication drivers;
10. OPC UA client/server module if applicable;
11. redundancy/HA license only if required;
12. installation, commissioning and training;
13. maintenance/support term and upgrade rights.

For each item classify:

- included in base license;
- separately licensed;
- quantity/concurrency based;
- free driver/module;
- TBD — vendor confirmation required.

## 8. Client and Large-Screen Licensing

Distinguish:

- full-control operator station;
- read-only client;
- browser/Web dashboard;
- unattended large-screen display.

Do not buy four full C/S control-client licenses if some stations are genuinely read-only and a lower-cost Web license meets the requirement. Conversely, do not downgrade a control station to Web only if reliable control functions are required.

For large screens, verify:

- concurrent Web sessions;
- browser compatibility;
- automatic login/session renewal;
- full-screen/kiosk operation;
- display refresh interval;
- whether a separate commercial BI license is needed.

## 9. Availability and Recovery

When SCADA is consolidated onto one server, explicitly state:

- server is a single point of failure;
- expected RTO/RPO;
- RAID protection;
- UPS graceful shutdown;
- backup schedule;
- restore test requirement;
- vendor spare/warranty response.

Only move to redundant SCADA/server architecture when the availability requirement justifies it.

## 10. Required Output

A project-level SCADA section should normally include:

- point-count assumptions and license tier;
- historian points, sampling assumptions and retention estimate;
- server resource assumptions;
- storage layout;
- client/Web/large-screen licensing;
- driver/protocol matrix;
- remote-control safety requirements where applicable;
- vendor confirmation items.

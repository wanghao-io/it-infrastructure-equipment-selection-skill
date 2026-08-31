# Server Sizing Reference

## Purpose

服务器选型必须从业务负载开始，而不是从型号、虚拟机数量或既有架构开始。

Use `scripts/calculate_server_capacity.py` for transparent CPU/memory estimates.

## 1. Choose the Sizing Mode

### Consolidated physical/server-service mode

Use when one physical server carries several services directly, for example:

- data acquisition;
- SCADA runtime;
- historian/database;
- alarm/event service;
- BI/reporting;
- Web publishing;
- integration/API services.

Estimate each service separately, then add OS overhead and explicit headroom.

### Virtualization mode

Use VM count/vCPU/VM memory only when the project is actually virtualized. Do not apply a vCPU overcommit model to a standalone physical SCADA/database server.

## 2. CPU

Consider:

- application/vendor minimums;
- database/historian load;
- acquisition/driver load;
- BI/report concurrency;
- Web users;
- peak rather than only average load;
- CPU architecture/OS compatibility;
- future growth/headroom.

Output:

- minimum supported configuration;
- recommended project configuration;
- upgrade trigger.

Do not equate logical vCPU with physical core without stating the virtualization/overcommit assumption.

## 3. Memory

Estimate:

```text
service working set
+ database/historian cache
+ OS/management overhead
+ explicit headroom
```

Memory is often a low-cost way to improve database/BI stability, but do not add capacity without a workload or growth reason.

## 4. Storage Layout

Separate where useful:

- OS/application;
- database/hot data;
- historical/archive data;
- backup.

Define:

- drive type;
- count;
- RAID level;
- usable capacity;
- controller/cache/power-loss protection;
- expected endurance/performance;
- independent backup target.

RAID is not backup.

## 5. Reliability

For a single-server production design explicitly check:

- redundant PSU where justified;
- enterprise drives/controller;
- RAID protection;
- UPS/graceful shutdown;
- independent backup;
- warranty/spares response;
- restore procedure and expected RTO/RPO.

A single server can be a valid budget architecture, but its single-point-of-failure risk must be stated rather than hidden.

## 6. Compatibility

Confirm before procurement:

- CPU architecture;
- supported OS;
- database version;
- SCADA/BI/vendor support matrix;
- NIC/storage-controller support;
- required management tools;
- warranty/support term.

For domestic/Xinchuang constraints, load `references/domestic-platforms.md` only when the project requires them.

For replacement/migration inventory use `references/brownfield-readiness.md`; for evidence of deployability and recovery use `references/acceptance-evidence.md`. Hardware field equality alone is not application/driver/license compatibility.

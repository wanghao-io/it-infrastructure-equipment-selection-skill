# Storage Sizing Reference

Storage selection must consider capacity, performance, reliability, retention and growth.

Use `scripts/calculate_storage.py` for RAID usable-capacity estimates and `scripts/calculate_historian.py` for SCADA historian retention estimates.

## 1. Capacity Layers

Keep these separate:

```text
Raw drive capacity
-> RAID/replication protected usable capacity
-> application/database usable allocation
-> retained business data
-> independent backup capacity
```

Do not report raw drive TB as usable project capacity.

## 2. RAID

For local server storage, state the exact RAID level and drive count.

Typical trade-offs:

- RAID1: simple mirror, useful for OS/small hot-data sets;
- RAID5: good capacity efficiency but write/rebuild risk must be considered;
- RAID6: two-parity protection with lower usable capacity;
- RAID10: strong write/rebuild behavior with 50% usable capacity.

Selection depends on workload, drive size, rebuild exposure, performance and budget. Do not declare one RAID level universally best.

If controller write-back cache is used for important database workloads, verify appropriate power-loss protection.

## 3. Retention Capacity

For history/log/archive workloads calculate from:

- daily ingest/growth;
- retention days/years;
- database/index overhead;
- expected growth;
- required free-space reserve.

For SCADA historians, calculate from **historical points and effective sample rate**, not total licensed tags. See `references/scada-sizing.md`.

## 4. Performance

Evaluate where relevant:

- IOPS;
- throughput;
- latency;
- read/write ratio;
- random vs sequential access;
- database checkpoint/log behavior;
- concurrent BI/report queries;
- SSD/NVMe endurance.

Use SSD for hot/current data when performance justifies it; use HDD/large-capacity media for archive when performance requirements allow.

## 5. Backup

Backup capacity is independent from the production RAID set.

Define:

- protected datasets;
- full/incremental schedule;
- retention/version count;
- restore point objective;
- restore test;
- whether an additional offline/offsite copy is required.

A NAS used as backup should not be counted as extra online historian capacity unless the architecture explicitly uses it that way.

## 6. Checklist

- exact drive model/type/count;
- RAID level;
- raw and usable TB;
- controller/cache/PLP;
- hot vs archive data placement;
- retention/growth assumption;
- free-space reserve;
- independent backup;
- restore test requirement.

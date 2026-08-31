# Acceptance Evidence and Production Readiness

Use for procurement acceptance criteria, compatibility claims, SCADA tests and retrospective evidence.
Use `assets/acceptance-evidence-example.json` with `schemas/acceptance-evidence.schema.json`.
Run `python3 scripts/infra_cli.py project-check acceptance-evidence acceptance.json`.
This validates recorded claim consistency, not external evidence authenticity or field acceptance.

## Test record

Record exact product/version/environment, stage, expected/tested scope, real or simulated workload, result, evidence references, adapters and unverified items.
Stages: smoke / mock / native / integrated / fat / sat / operation.
FAT/SAT labels alone are insufficient: record the real equipment/configuration and actual acceptance scope in the linked evidence.
Do not inherit PASS after a firmware/OS/driver/configuration change without checking its impact.

An adapter-assisted PASS is not a native-compatibility PASS. Preserve native failure, record adapter version/owner/support/cost/performance, and evaluate the allowed solution separately.
Only a scoped test with accepted dependencies may pass for that solution. No automatic site connection or physical-control test is authorized by this reference.

## SCADA count ledger

Keep source-declared, actually read, deduplicated, external IO, charged system points, IO-mapped, GOOD, historical target/tested, display bindings and simulated points distinct.
The v1 ledger is a compact count reconciliation, not a universal point-table importer or proof of unique-point mapping.
A source count mismatch needs investigation. Same-name points across devices and missing acquisition start/stop conditions block the affected final configuration.
License demand includes only vendor-confirmed chargeable categories; unknown system-point charging remains CONDITIONAL.
Do not drop required business IO to fit a purchased tier.
Historical sampling classes remain in the historian sizing record, not a single arithmetic-average interval.

## Production authorization

Freeze trial/development/production status, expiry/perpetual evidence, hardware binding, offline activation, reissue timing, virtualization/migration/HA rights and owner.
Count clients as named/concurrent according to vendor terms; record driver/API/ODBC modules separately.
A running process or HTTP 200 is smoke evidence only; verify actual acquisition, historical writes, restart recovery and effective authorization.
A successful import is not IO mapping, GOOD acquisition or historical completeness.
Two sampled points cannot prove a full historian; visual particles are not actual IO throughput.

## Performance and recovery

Record server/client configuration, colocated simulators, real devices, batches/sample periods, concurrent historian/reporting/display work, endpoints, duration, latency percentiles and resource use.
Do not equate parallel HTTP requests with simultaneous operators.
Only verify GPU/browser/3D performance when such a display workload is actually required.
For replacement/restore planning load `references/brownfield-readiness.md`: image extraction or boot success is not business recovery.

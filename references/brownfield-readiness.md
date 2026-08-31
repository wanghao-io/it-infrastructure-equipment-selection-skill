# Brownfield Replacement and Recovery Readiness

Use for replacing, migrating or extending an existing system. This is a procurement/readiness route, not an automated repair runbook.

Inventory exact application/driver/database versions, CPU ISA, OS/kernel and 32/64-bit dependencies.
Record DSN/configuration references, not passwords. Credentials and keys remain in authorized secret storage.
Check physical/virtual hardware support, boot mode, storage/NIC drivers, peripherals/dongles and license rebinding.
Collect installation media, dependencies, configuration, point tables, source programs where contracted, database backups, system images and VM configuration.

RAID protects against specified disk failures, not all controller/firmware faults or data loss.
Confirm compatible controller/spares and vendor-supported recovery procedure; do not infer support from a matching connector.
Map backups to system/data/boot/configuration/license coverage. A WIM or one configuration export is not a complete recovery package.

Before purchase agree RTO/RPO, recovery hardware, change window, business/data consistency checks, rollback trigger and responsible party.
Acceptance ends at restored business functions and verified data, not image deployment, OS startup or DSN connectivity.
Record actual recovery evidence with acceptance-evidence; absent tests remain CONDITIONAL.

Do not execute partitioning, RAID import, credential extraction, registry changes or production writes from this route.
Such work requires a separate explicit operational task, suitable tools, backup and authorization.

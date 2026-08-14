# Schema Governance

## Compatibility policy

- Treat the unversioned schema paths with `schema_version: 1` as frozen v1 contracts.
- Put breaking changes under `schemas/v2/` with versioned `$id` values.
- Read `schemas/catalog.json` for current, supported and deprecated contract versions.
- Reject future or unknown versions clearly; do not guess compatibility.
- Keep golden v1 examples valid while their version remains supported.

## Migration policy

Use `scripts/migrate_schema.py` for supported migrations. It prints a dry-run report by default, never edits the source, and refuses to overwrite an existing output. Migration may rename or structurally relocate known values, but must never invent `PASS`, `Verified`, zero, a supplier identity, decision scope or current date.

Price-evidence v2 adds one explicit decision scope and makes technical-fit fields mandatory. Project-retrospective v2 supports structured operational measurements and normalized commercial/technical scope declarations. Passing a schema confirms structure only; it does not prove engineering suitability or evidence truth.

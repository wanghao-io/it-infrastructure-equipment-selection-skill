# Private Extensions

Use this boundary when a company needs private templates, supplier quotations or product facts.

## Non-negotiable boundary

- Keep the public Skill checkout clean and fast-forwardable.
- Store private templates and adapters in a separate private repository.
- Store raw quotations, contacts, customer identifiers and contracts in an access-controlled data source, not either code repository.
- Load a private extension only from an explicit path supplied for the current task. Do not scan home directories, environment variables or adjacent folders automatically.
- Namespace private template IDs, reject collisions and never allow a template to weaken Mandatory gates, evidence rules or TBD handling.

## Quote ingestion

Treat supplier files as raw facts. Allow price, currency, dates, supplier/channel identity, configuration text and source provenance. Strip or reject supplier-supplied decision fields such as `technical_fit_status`, `eligible_for_pricing`, `comparable`, `exact_configuration_match` and evidence level; derive those only after independent engineering checks.

Apply column allowlists, row/file/string size limits, ISO dates, three-letter currencies and formula/macro rejection. Preserve source-file hash and row number in the private audit record. Normalize supplier identity before counting independent evidence. Never echo contacts, customer names or full quotation contents in public logs.

## Compatibility

Declare a core version range in a private extension manifest and validate it before use. Migrate schemas explicitly; never fill unknown values with `PASS`, `Verified`, zero or the current date. Temporary exports should use restricted permissions and be removed after the task.

The public project intentionally provides the contract and boundary, not an automatic private-data loader.

# Project Evidence and Handoff

Use only for multi-source projects, revisions or handoff. A single calculation does not require a project manifest.

## Explicit input boundary

Use `assets/project-evidence-example.json` and `schemas/project-evidence.schema.json`.
Record project/baseline IDs, sources, file version and SHA-256, conversion origin, field authority, facts and exact locators.
Declare read-only sources, allowed output directories and protected paths. Do not discover private files outside the explicit task scope.
Sources are automatically protected against output overwrite; do not also list a readable source in protected_paths merely to make it read-only. protected_paths means NO ACCESS (read or write), for example another agent's output. A refusal from the path guard is not permission to retry with a lower-level file/hash tool. Correct an accidentally contradictory manifest from the user's intended scope, or leave the source unavailable.
A null fingerprint is unresolved, not a fabricated checksum. The example is synthetic and intentionally incomplete.

Run `python3 scripts/validate_project_delivery.py project-evidence manifest.json`.
Add `--project-root /explicit/project --check-files` only when authorized to read listed source files. The default validates records without opening those sources.
The validator checks declared authority/relationships, not whether the source assertion is true.

## Field-level authority

- Drawings may establish geometry; equipment schedules may establish quantities; quotations establish commercial scope.
- A conversion records its original source and limitations. File modification time does not determine engineering authority.
- A user's confirmed connection updates that connection only, not cable length, protocol or compatibility.
- A presentation-only removal does not establish that equipment is absent on site.
- A previously recommended option is not a locked requirement.
- Unknown facts remain unresolved; assumptions are not automatically upgraded by repeated use.
- Two active, conflicting values require a decision. Do not choose whichever file is newest.
- Supersession requires a matching entity/field, explicit old disposition and an approval reference; preserve the old record.
- Locked architecture constraints remain in force until an authorized requirement change. Minimum architecture does not mean removing explicitly required redundancy.

## Compact handoff

Keep only current objective, baseline/source references, confirmed constraints, completed checks, remaining work and protected paths.
Link detailed evidence rather than copying a long chat. Do not include credentials.
If another agent changes the source fingerprint, re-evaluate affected facts and downstream artifacts; do not overwrite that agent's work.
Approval to continue does not authorize production control, public disclosure, purchasing or bypassing review policies.

## Output

Report changed facts, superseded facts, conflicts, owners and affected calculations/BOM/diagrams/tests.
`PASS` means record consistency only. `CONDITIONAL` permits a labeled draft, not a final procurement conclusion.

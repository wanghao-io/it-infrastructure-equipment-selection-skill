# Project delivery improvements — implementation record

Date: 2026-08-31. Status: prepared for v1.6.0, based on v1.5.0 (`4cbc67e`).
The records below describe the development checks. Actual publication is governed by the tag Release workflow; these records do not update installed user skills or production systems.

## Delivered scope

| Plan area | Implementation | Evidence |
|---|---|---|
| Quote identity / commercial basis | Minimum fit is separate from exact declared fields; mixed tax/delivery declarations cannot be normalized by a shared scope ID | QuoteAndBudgetRepairTests R01/R02 |
| Budget arithmetic / draft | Decimal quantity/unit/total reconciliation, explicit lump-sum note, draft/RFQ TBD export, no procurement certification from rendering | R03/R04 plus decimal and CLI output tests |
| Copy update protection | Full runtime stage/hash/AST validation, manifest/local-change check, rollback on replacement failure, Git identity/origin policy | InstallerUpdateTests including injected copy/swap failures |
| Project evidence | Independent strict v1 contract, source/field authority, conflicts/supersession, no-access paths, optional explicit file hash check | ProjectEvidenceTests R05–R07 |
| Delivery alignment | Complete asset projections, phases, optional state, material/license dependencies, explicit PoE and license capacity | DeliveryTests R08–R13 |
| Draw.io | Optional plain-shape logical draft, group clone helper, structure and presentation-only semantic checks | XML/semantic/group tests; separate local render inspection |
| Compliance | Capability/implementation/verification/owner/action matrix and survey template | Routed reference and independent phased-factory evaluation |
| Software/acceptance/recovery | Version/adapter/coverage/production-license records, point ledger, recovery readiness reference | AcceptanceTests R15–R18 and independent SCADA/recovery evaluations |
| Evidence honesty | Original v1.5 plan and question-bank test renamed/reclassified; no raw private transcripts copied into this repo | docs/v1.5-plan.md; scenario evaluation record |

## Deliberate boundaries

- V1/V2 published schemas remain unchanged. Three new record families are separately named v1 contracts. Semantic checks run through `project-check`; ordinary Schema success remains structural only.
- Server RFQ v2 still covers its declared fields only. It does not encode every chassis order code, regional warranty or license policy. Exact equality and matching text do not independently verify quotations; unresolved external scope stays CONDITIONAL in the procurement workflow.
- Project delivery checks caller-supplied normalized projections, not automatic extraction of every Word/Excel/Draw.io file. A projection must be reconciled with actual source/export data.
- Draw.io CLI produces a logical draft, not CAD reconstruction or surveyed physical routing. The group-clone function is available to explicit adapters; the CLI does not automatically choose/import vendor icons. Dense graph layout and style-encoded engineering meaning require rendered/manual review.
- `protected_paths` prohibits both reads and writes. Readable source files are automatically protected from output overwrite; do not label them no-access simply to make them read-only.
- Draft/RFQ rendering may retain unknown prices. `budget-complete` only establishes arithmetic completeness, not procurement-ready status. Monetary arithmetic currently uses two-decimal rounding; currencies needing another exponent require an explicit future contract.
- Compliance clauses, current prices, native driver compatibility and field recovery still need appropriate external evidence. No production operations or automatic supplier outreach are added.
- Real quotations/awards/settlement/operation evidence and second-human stewardship remain evidence-dependent. No synthetic test satisfies those claims.

## Reproduce

```bash
python3 -m unittest discover -s tests
python3 scripts/validate_json_schemas.py --catalog
python3 scripts/validate_release.py
python3 scripts/infra_cli.py project-check project-delivery assets/project-delivery-example.json
python3 scripts/infra_cli.py project-check project-evidence assets/project-evidence-example.json
python3 scripts/infra_cli.py project-check acceptance-evidence assets/acceptance-evidence-example.json
```

The last two intentionally return CONDITIONAL/nonzero: templates have incomplete evidence and no executed field tests. This is expected, not a broken installation.
Test-only fixtures use temporary directories; no customer project directories or protected agent outputs are part of CI.

## Validation log

Validation is recorded after commands/evaluations actually finish. See `docs/project-delivery-forward-evaluation.md` for synthetic Agent outcomes and limits; these are not external-user or production acceptance records.

Final local check: **188 tests passed**, Schema catalog passed, release-metadata consistency passed, Skill quick validator passed, compileall and diff checks passed. Environment: Darwin, Python 3.11.7. This is not a new Linux/Windows CI run.

A clean temporary copy install and subsequent managed update both completed; the installed project-check command passed its synthetic delivery example. Staged Agent Skills publish dry-run succeeded with the advisory warnings documented in the forward-evaluation record. No real publish or user-level installation update was performed.

Runtime snapshot: 111 managed files; SHA-256 of the sorted per-file hash map: `8414a912562499c924c9b319f246f96deba5da96be93a0722db621dfb419872a`. This records the final development runtime, not a signed/tagged release. The Router is 207 lines; existing released v1/v2 schema files were not modified.

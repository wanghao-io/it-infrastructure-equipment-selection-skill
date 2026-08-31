# IT Infrastructure Equipment Selection Skill v1.6.0

## Project delivery without weakening engineering gates

- New independent `project-evidence-v1`, `project-delivery-v1` and `acceptance-evidence-v1` contracts, examples and `infra_cli.py project-check` checks. Simple selection and calculators do not require them.
- Source authority, field-level changes, protected paths, asset/BOM/phase projections, material/license dependencies, PoE capacity and verification scope are explicit and checkable.
- Optional Draw.io logical drafts, group cloning and presentation-only semantic checks. Rendering, dense-graph review and physical surveys remain separate tasks.
- Compliance implementation, survey, software-license/point-count and brownfield recovery guidance connect procurement requirements to owners and acceptance evidence.

## Correctness and update safety

- A minimum server-capacity PASS no longer makes an upgraded configuration an exact price anchor. Matching scope IDs cannot conceal different tax/delivery declarations.
- BOM arithmetic reconciles quantity, unit price and total using Decimal rounding. Draft/unpriced RFQ output retains TBD values and never certifies procurement readiness.
- Copy installs use complete staged validation, managed-file hashes and rollback. Git updates check Skill identity and trusted origin while retaining dirty-tree and fast-forward protections.
- Unknown endpoint totals remain null; source read-only protection is distinct from no-access paths. Earlier scenario/implementation claims are explicitly corrected.

## Compatibility and limits

- Existing released v1/v2 Schema files remain unchanged. New record families have separate v1 contracts.
- Legacy copied installs without a manifest require inspection and explicit `--force`; modified managed files are not silently overwritten.
- RFQ v2 and project validators check declared fields/projections, not every vendor option code, external evidence truth or formal compliance. Matching records do not establish current orderability, native compatibility or field acceptance.
- The five Agent cases are synthetic evaluations, not external adoption or actual procurement accuracy. Public field evidence and human bus factor claims are unchanged.
- No product database, crawler, production control, automatic supplier outreach or public-data upload is added.

## Validation

The development record includes 188 passing local tests, five independent synthetic scenarios with documented rechecks, a local Draw.io render inspection, clean copy installation/update and Agent Skills dry-run. The tag pipeline requires Linux/macOS/Windows × Python 3.10/3.12, complete Schema checks, archive smoke tests and SHA-256 generation before publication.

See `docs/project-delivery-implementation.md` and `docs/project-delivery-forward-evaluation.md` for the exact evidence scope and limitations.

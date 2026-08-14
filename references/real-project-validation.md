# Real-project validation and anonymized retrospectives

Use real cases to test whether the workflow survives incomplete drawings, saved budgets, current quotations and commercial-scope ambiguity. Synthetic regression tests remain necessary, but they do not prove field accuracy.

## Evidence stages

Keep the stage explicit:

- `design-baseline-only`: requirements, design and budget revisions only;
- `current-quotes`: dated configuration-matched quotations exist;
- `award-record`: a purchase award or signed order exists;
- `settlement-record`: final commercial settlement exists;
- `operational-measurement`: post-implementation capacity, availability or power data exists.

Never describe a design-stage variance as procurement forecast accuracy. Only compare forecast with award/settlement when the technical and commercial scope is normalized.

## Minimum retrospective

Record:

1. anonymized facts and source-artifact types;
2. project stage and evidence status;
3. initial, revised, awarded and settled values only when actually known;
4. configuration and commercial-scope changes;
5. error attribution: quantity, specification, license, accessory, tax, delivery, implementation, contingency or market movement;
6. workflow rule changes and regression coverage;
7. limitations and unresolved evidence.

Validate a structured retrospective with `schemas/project-retrospective.schema.json`.

## Anonymization

Remove customer, personal, supplier-contact and sensitive-location identifiers. Generalize distinctive process details when they are not necessary to explain the engineering lesson. Do not publish raw quotations, credentials, network addresses, CAD drawings or proprietary point lists.

## Included real cases

- `examples/real-project-retrospectives/manufacturing-scada-budget-revision.json`
- `examples/real-project-retrospectives/smart-factory-network-design.json`

Both are honestly labeled `design-baseline-only`; neither claims an award, settlement or operational result.

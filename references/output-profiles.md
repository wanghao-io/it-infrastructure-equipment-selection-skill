# Output Profiles

Choose the output profile from the user's actual stage. Do not produce every artifact by default.

## 0. Optional decision summary

For a project-level answer, place a one-page decision summary before the selected detailed profile:

1. current conclusion and decision state;
2. facts and configurations that can be frozen now;
3. Mandatory blockers and decisions awaiting evidence;
4. the 3–7 confirmations most likely to change architecture, eligibility or budget;
5. a compact assumption/evidence ledger;
6. links or appendix references to unchanged calculations, BOM, evidence and acceptance detail.

The summary is a presentation layer, not a replacement for engineering evidence. Never hide `CONDITIONAL`, exclusions or incomplete commercial scope to make it shorter.

## 1. quick-selection

Use for a single device or fast shortlist.

Output:

- requirement summary;
- minimum/recommended configuration;
- 2–4 candidate models if research is requested;
- approximate market range;
- key risks / confirmation items.

Avoid long architecture discussions unless they change the selection.

## 2. internal-review

Use for project planning, internal budget review or technical discussion.

Output normally includes:

1. known conditions;
2. assumptions;
3. TBD items;
4. architecture decisions and why complexity is included/excluded;
5. capacity basis;
6. recommended equipment/software configuration;
7. logical topology when useful;
8. budget/BOM with evidence type;
9. compressible/optional items;
10. risks and upgrade triggers.

Budget should normally include a contingency percentage when requested or appropriate.

## 3. procurement-rfq

Use when the next action is supplier quotation or tender preparation.

Prioritize measurable and vendor-neutral content:

- item/category;
- technical requirements;
- quantity/unit;
- Mandatory / Recommended / Optional classification;
- licensing quantity/concurrency;
- included accessories;
- warranty/support;
- supplier response column;
- deviation column;
- required evidence;
- commercial assumptions that must be quoted separately.

Avoid explanatory prose that suppliers do not need.

## 4. detailed-design

Use after products/architecture are substantially confirmed.

May include:

- physical/logical topology;
- VLAN/subnet/IP plan;
- port allocation;
- rack layout;
- power/UPS load;
- storage/RAID layout;
- backup schedule;
- SCADA protocol/tag/driver matrix;
- acceptance/FAT/SAT test cases;
- implementation and rollback plan.

Do not invent design details that have not been confirmed.

## 5. compliance-check

Use against a tender/RFQ or proposed supplier response.

Output:

| Requirement | Priority | Supplier response | Evidence | Result | Deviation/Risk |
|---|---|---|---|---|---|

Results:

- PASS;
- CONDITIONAL;
- FAIL;
- NEEDS CONFIRMATION.

Mandatory failures cannot be hidden by an overall weighted score.

## 6. bom-budget

Use when cost is the primary deliverable.

Recommended CSV fields:

```text
序号,类别,设备/服务,配置或范围,数量,单位,估算单价（元）,估算合计（元）,价格口径,证据等级,参考来源,备注
```

For Chinese Excel delivery, prefer UTF-8 with BOM (`utf-8-sig`).

Include:

- recommended subtotal;
- contingency amount/percentage;
- total budget;
- optional/compressible items;
- excluded scope;
- pricing date and evidence caveat.

## 7. Mode Combination

Profiles can be combined when useful, for example:

- `internal-review + bom-budget`;
- `procurement-rfq + tender-spec`;
- `detailed-design + topology-generation`;
- `compliance-check + vendor-compare`.

The selected profile controls **format and depth**, not architecture. Architecture still follows requirements.

## Project delivery refinements

- A technical draft or unpriced RFQ is useful when prices are deferred; do not invent prices to finish a CSV.
- Distinguish declared-record consistency, engineering eligibility, implementation, test coverage and formal acceptance.
- For remediation use `references/compliance-implementation.md`, not one combined satisfaction score.
- For multi-source changes use `references/project-evidence.md`; for artifact/phase alignment use `references/project-delivery.md`.
- Preserve user-approved fonts and untouched content; presentation-only changes cannot mutate device/edge semantics.
- Ask the highest-impact questions once, associate an owner and downstream decision, and carry unresolved answers explicitly. Do not require a full project manifest for a simple calculator.

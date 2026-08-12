# Guided Requirements, Scenario Templates and Recommendation Rules

Use this reference when the user gives a broad project description, asks for an end-to-end recommendation, or wants multiple alternatives ranked.

The goal is to reduce repeated questioning without turning a scenario label into a predefined architecture.

## 1. Scenario templates are discovery aids, not architectures

Structured templates live in:

```text
assets/scenario-templates.json
```

Current templates include:

- `generic-infrastructure`
- `manufacturing-scada-small`
- `smb-erp`
- `virtualization-small`
- `vdi-small`
- `edge-computing`
- `backup-storage`

A template may provide:

- a concise scenario description;
- suggested planning assumptions such as growth margin or planning horizon;
- high-value requirement questions;
- scenario-specific guardrails.

A template must **not** silently decide:

- HCI versus standalone/virtualization;
- HA/N+1;
- dual-core switching;
- firewall/security appliances;
- domestic/Xinchuang platform;
- GPU/AI infrastructure;
- a particular vendor/model.

User/project facts always override template suggestions.

## 2. Guided requirement discovery

When the request is under-specified but the scenario is clear, load the closest template and ask only the highest-value unresolved questions.

Use:

```bash
python3 scripts/guide_requirements.py --list
```

Then, for example:

```bash
python3 scripts/guide_requirements.py \
  --scenario manufacturing-scada-small \
  --input project-known-fields.json \
  --max-questions 7 \
  --pretty
```

The helper returns:

- known fields;
- missing required fields;
- the next concise questions;
- suggested assumptions;
- guardrails;
- `ready_for_architecture`.

Rules:

1. Do not ask again for facts already supplied by the user or project files.
2. Prefer 3–7 high-value questions over a long questionnaire.
3. Separate `known`, `assumed`, and `TBD`.
4. Suggested assumptions are not facts. If they materially affect architecture, capacity, safety, compliance or price, surface them explicitly.
5. Do not block low-risk progress on every minor TBD; use explicit assumptions where reasonable.
6. Do block product recommendation when a missing Mandatory requirement would change technical eligibility.

## 3. Constraint engine: hard filters before preference scores

Recommendation flow:

```text
candidate facts
      ↓
Mandatory constraints
      ↓
PASS / CONDITIONAL / FAIL
      ↓
preference scoring only for comparison
      ↓
recommendation order
```

`FAIL` candidates are excluded.

`CONDITIONAL` means a Mandatory attribute is unresolved. A higher preference score must not place a CONDITIONAL candidate above a PASS candidate.

Use optional top-level `constraints` in `scripts/compare_vendors.py`:

```json
{
  "constraints": [
    {
      "key": "memory_gb",
      "name": "Memory >= 128 GB",
      "operator": "min",
      "value": 128,
      "severity": "mandatory"
    },
    {
      "key": "domestic_cpu",
      "name": "Domestic CPU required",
      "operator": "eq",
      "value": true,
      "severity": "mandatory"
    }
  ],
  "criteria": [
    {"key": "tco", "name": "5-year TCO", "weight": 30},
    {"key": "lifecycle", "name": "Lifecycle", "weight": 25},
    {"key": "operability", "name": "Operability", "weight": 25},
    {"key": "expansion", "name": "Expansion", "weight": 20}
  ],
  "candidates": [
    {
      "name": "Candidate A",
      "attributes": {
        "memory_gb": 128,
        "domestic_cpu": true
      },
      "scores": {
        "tco": {"score": 8, "evidence": "Verified"},
        "lifecycle": {"score": 9, "evidence": "Verified"},
        "operability": {"score": 8, "evidence": "Estimated"},
        "expansion": {"score": 8, "evidence": "Verified"}
      }
    }
  ]
}
```

Supported constraint operators:

- `eq`
- `ne`
- `min`
- `max`
- `in`
- `contains`
- `truthy`
- `falsy`

Keep rules project-specific. Do not encode permanent vendor reputations or brand rankings.

## 4. Preference scoring

Use weighted scores only after Mandatory fit.

Typical preference dimensions:

- TCO;
- lifecycle/support horizon;
- operability and maintenance complexity;
- expansion headroom;
- energy/power density;
- current price evidence quality;
- implementation complexity;
- compatibility with the existing environment.

Scoring rules:

- use 0–10 consistently;
- record evidence beside every material score;
- do not hide a price-evidence weakness inside a single composite score;
- do not give precise scores when the underlying evidence is weak;
- explain why the top PASS candidate wins.

## 5. TCO

When acquisition price alone could distort the decision, load `references/tco.md` and use `scripts/calculate_tco.py`.

TCO is a preference/cost dimension. It does not override technical, safety, compliance or lifecycle Mandatory requirements.

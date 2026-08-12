---
name: it-infrastructure-equipment-selection
description: >
  IT infrastructure solution architect skill for selecting, sizing, validating and budgeting
  physical infrastructure equipment. Use for equipment selection, BOM generation, tender/RFQ
  compliance checks and specification generation, project infrastructure planning, alternative model
  research, vendor/model comparison, price research, network topology generation and industry reference
  designs. Choose architecture patterns and platform constraints only when required by the project;
  HCI, domestic/Xinchuang platforms, industrial IT/OT patterns and other specialized designs are optional,
  not default requirements.
---

# IT Infrastructure Equipment Selection

## Role

Act as a senior IT infrastructure solution architect.

## Workflow

1. Understand project requirements and business workload
2. Identify hard constraints, soft preferences, assumptions and unknowns
3. Decide which architecture patterns are actually needed
4. Calculate capacity requirements
5. Define minimum and recommended specifications
6. Research current products and verify official specifications
7. Validate lifecycle, compatibility and market availability
8. Research price evidence using authoritative and comparable sources
9. Compare cost, reliability, lifecycle, operability and expansion capability
10. Generate only the artifacts required by the task: recommendation, matrix, tender specification, topology, BOM, budget or compliance report

## Architecture Decision Rule

Do not force a predefined architecture.

Treat the following as optional solution patterns that are loaded only when project requirements justify them:

- Hyper-converged infrastructure (HCI)
- Traditional virtualization + shared storage
- Standalone physical servers
- Cloud or hybrid infrastructure
- Industrial IT/OT segmented architecture
- Domestic/Xinchuang hardware and software platforms
- High-availability clusters
- GPU/AI infrastructure

Examples:

- Do not recommend 3-node HCI merely because virtualization is required.
- Do not apply domestic/Xinchuang constraints unless the user, tender, policy or project context requires them.
- Do not introduce HA, dual-core networking, redundant firewalls or N+1 unless availability requirements justify the cost.

When several architectures are feasible, compare them and explain why one is preferred.

## Evidence and Procurement Research

For equipment selection and budget work, separate four questions:

1. **Technical fit** — does the exact model/configuration meet the requirement?
2. **Lifecycle and availability** — is it current, orderable and supportable?
3. **Market price** — what is a realistic current purchasing range?
4. **Comparable transaction evidence** — what have similar configurations actually been purchased for?

Use `references/procurement-research.md` for the detailed source hierarchy and search workflow.

Key rules:

- Technical specifications: prefer manufacturer product pages, official datasheets, configurators, compatibility matrices and support/lifecycle notices.
- Historical procurement price: prefer official government procurement award/transaction records when a genuinely comparable configuration exists.
- Current enterprise market price: use authorized channels and enterprise procurement platforms as secondary evidence.
- Never treat a marketplace title or reseller description as the sole proof of a critical technical specification.
- Record the exact configuration, source date, tax/service assumptions and evidence quality for every important price.
- If prices are not configuration-comparable, report a range and explain the uncertainty instead of averaging them blindly.

## Optional Artifact Modes

Load and use these only when the user requests the corresponding artifact or when it is directly useful to the stated goal.

### vendor-compare

Use `references/vendor-comparison.md` and optionally `scripts/compare_vendors.py`.

Rules:

- Compare project-specific candidate configurations, not brand reputation.
- Define mandatory knockout gates before weighted scoring.
- A failed mandatory requirement always results in `FAIL`; scoring cannot override it.
- Normalize exact configured BOM, licenses, support and lifecycle before price comparison.

### tender-spec

Use `references/tender-specification.md` and optionally `scripts/generate_tender_spec.py`.

Rules:

- Convert engineering needs into measurable, vendor-neutral procurement requirements.
- Classify requirements as Mandatory / Recommended / Optional.
- Include acceptance/evidence requirements for critical clauses.
- Avoid locking to a brand/model or proprietary feature unless explicitly justified.
- Mark unresolved details as TBD instead of inventing them.

### topology-generation

Use `references/network-topology.md` and optionally `scripts/generate_topology.py`.

Rules:

- Generate a logical topology first.
- Prefer Mermaid for Markdown/GitHub-native diagrams; support Graphviz DOT when useful.
- Do not invent VLAN IDs, IP addresses, physical ports, redundant links or security zones.
- Keep topology consistent with the selected architecture and BOM.

### reference-design

Use the closest file under `examples/` as a method template, then adapt it to the user's actual requirements.

Rules:

- Examples are references, not mandatory architectures.
- Do not copy example capacities or redundancy into a new project without recalculation.
- Preserve anonymization when creating public examples.

## Principles

- Requirements first, products second
- Architecture follows requirements; do not force HCI, Xinchuang or any other pattern
- Do not reverse engineer requirements from a product
- Separate verified specifications from estimates
- Separate technical evidence from price evidence
- Prefer official datasheets for technical facts
- Compare exact configurations, not just chassis/model families
- Treat vendor comparison scores as project-specific, not permanent brand rankings
- Keep tender parameters vendor-neutral unless a restriction is justified
- Do not invent topology details that are not known
- Identify risks and unknowns clearly

## Task Modes

- single-device: single equipment selection
- project-design: complete infrastructure planning
- compliance-check: tender/RFQ parameter validation
- bom-budget: equipment list and cost estimation
- alternative-search: compare replacement models
- price-research: market price and comparable transaction investigation
- vendor-compare: project-specific vendor/model comparison matrix
- tender-spec: generate tender/RFQ technical parameters and supplier compliance table
- topology-generation: generate logical network topology in Mermaid or Graphviz DOT
- reference-design: build a requirement-driven industry reference design from anonymized examples

## Output

Provide only the sections needed for the task. For a full project, normally include:

1. Requirement analysis
2. Design assumptions and constraints
3. Architecture decision (only where relevant)
4. Capacity calculation
5. Technical recommendation
6. Candidate products and evidence
7. Selection rationale or vendor/model matrix when requested
8. Tender/RFQ parameters when requested
9. Logical topology when requested
10. BOM and budget range
11. Risks, uncertainty and confirmation items

Load detailed calculation, procurement, comparison, tender or topology rules from references only when required.

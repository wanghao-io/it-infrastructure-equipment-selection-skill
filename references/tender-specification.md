# Tender / RFQ Specification Generation

Use this reference when the user asks to generate technical tender parameters, RFQ specifications, purchase requirements, or a compliance checklist from project needs.

## Principle

Write requirements around capabilities, measurable performance, interfaces, reliability and support. Do not unnecessarily lock to one vendor, model or proprietary feature.

Only include a brand/model restriction when the user explicitly requires it or when compatibility with an existing installed base makes it technically necessary. State the reason.

## Workflow

1. Extract project goals and mandatory constraints.
2. Separate confirmed facts from assumptions and unresolved items.
3. Convert engineering needs into measurable procurement parameters.
4. Classify clauses as `Mandatory`, `Recommended`, or `Optional`.
5. Add acceptance/evidence requirements for critical clauses.
6. Check for contradictions, impossible combinations and hidden accessories/licenses.
7. Produce a compliance table that suppliers can answer item by item.

## Parameter categories

Use only relevant categories.

### General

- Equipment type and quantity
- Deployment environment
- Form factor / rack requirements
- Power supply and redundancy
- Operating temperature where relevant
- Warranty and support term

### Compute

- CPU architecture if genuinely required
- Minimum physical core count
- CPU socket / expansion requirement if relevant
- Memory capacity and expansion slots
- Boot/system storage
- Data storage
- RAID/HBA requirement
- Network interfaces
- Out-of-band management

### Storage

- Raw and usable capacity definitions
- Media type
- Data protection scheme
- Performance / latency / IOPS requirement where justified
- Controller / path redundancy
- Expansion capability

### Network

- Access/uplink port quantity and speed
- Optical/electrical interface type
- Switching capacity / forwarding performance where relevant
- L2/L3 features actually needed
- Stacking/MLAG/redundancy where required
- Management and telemetry

### Firewall / security appliance

- Required throughput with the necessary security services enabled
- Concurrent sessions / new sessions when relevant
- VPN requirements
- Interface requirements
- HA mode if required
- Subscription/license term

### UPS

- Rated kW and kVA
- Power factor
- Topology
- Input/output phase
- Runtime at stated load
- Battery cabinet and bypass requirements

## Neutral wording examples

Prefer:

- `Single server shall provide not less than 24 physical CPU cores.`
- `The system shall provide at least two 10GbE data interfaces and separate management connectivity.`
- `Threat-protection throughput shall meet the stated value with required IPS/application/security services enabled.`

Avoid unless explicitly justified:

- `Must use CPU model X.`
- `Must be vendor Y model Z.`
- `Must support proprietary feature Q` when an interoperable capability would meet the need.

## Compliance output

Recommended columns:

| ID | Requirement | Level | Supplier response | Evidence | Result | Notes |
|---|---|---|---|---|---|---|

Result values:

- `Meets`
- `Partially meets`
- `Does not meet`
- `Needs confirmation`

## Quality checks

Before finalizing:

- Verify every numeric threshold has an engineering reason.
- Avoid mutually conflicting minimum/maximum values.
- Ensure dimensions, units and interface generations are unambiguous.
- Specify whether capacity is raw or usable.
- Specify whether price includes tax, licenses, accessories, implementation and support.
- Ensure the specification does not accidentally exclude equivalent products without justification.
- Mark uncertain project details as `TBD` rather than inventing them.

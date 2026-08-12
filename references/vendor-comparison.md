# Vendor and Model Comparison Framework

Use this reference only when the task requires comparing multiple vendors, product families, or exact configurations.

## Goal

Build a traceable comparison matrix based on project requirements and evidence, not on generic brand reputation.

Do not assign a permanent score to a vendor. Score the **specific candidate configuration for the specific project**.

## Comparison sequence

1. Extract hard requirements and soft preferences.
2. Define knockout criteria before scoring.
3. Normalize each candidate to an exact comparable configuration.
4. Verify critical specifications using official evidence.
5. Mark evidence quality and unresolved items.
6. Apply PASS / CONDITIONAL / FAIL gates.
7. Score only candidates that pass the hard gates.
8. Explain trade-offs and recommend a shortlist, not a universal winner.

## Hard gates

Typical hard gates include:

- Required CPU architecture or software compatibility
- Minimum physical cores / memory / usable storage
- Required interface type and quantity
- Required throughput with specified security features enabled
- Required redundancy or availability capability
- Required certifications or operating-system support
- Required warranty/support term
- Lifecycle and orderability constraints
- Mandatory tender clauses

If a hard gate is not met, mark the candidate `FAIL` even if its weighted score would otherwise be high.

If a hard gate depends on an optional module, license, firmware level, or unverified statement, mark it `CONDITIONAL` until verified.

## Suggested weighted criteria

Weights are project-specific. A reasonable starting set is:

| Criterion | Typical range | Notes |
|---|---:|---|
| Requirement fit | 25-40% | Exact technical fit and headroom |
| Lifecycle / availability | 10-20% | Current generation, support horizon, supply |
| Reliability / serviceability | 10-20% | Redundancy, hot swap, service model |
| Expansion capability | 5-15% | Slots, ports, DIMMs, drive bays, licensing |
| Compatibility / ecosystem | 5-15% | OS, hypervisor, management, peripherals |
| Operability | 5-15% | Management, monitoring, maintainability |
| Cost / TCO | 10-25% | Hardware + license + support + accessories |
| Evidence confidence | 5-10% | Quality of verified source material |

Do not use all criteria automatically. Remove irrelevant ones and redistribute weights.

## Evidence levels

- `Verified`: manufacturer documentation or authoritative compatibility/lifecycle source confirms the exact point.
- `Market-verified`: current authorized/enterprise market evidence confirms availability or price.
- `Estimated`: engineering estimate based on known inputs.
- `Assumption`: project information is missing and an assumption was necessary.
- `Needs confirmation`: vendor/channel confirmation is still required.

## Matrix format

Recommended output:

| Criterion | Weight | Candidate A | Evidence | Candidate B | Evidence | Candidate C | Evidence |
|---|---:|---:|---|---:|---|---:|---|
| Requirement fit | 35 | 9.0 | Verified | 8.0 | Verified | 7.0 | Needs confirmation |
| Lifecycle | 15 | 8.0 | Verified | 9.0 | Verified | 6.0 | Market-verified |
| Cost / TCO | 20 | 7.0 | Market-verified | 8.5 | Market-verified | 9.0 | Estimated |

Then provide:

- Gate result: PASS / CONDITIONAL / FAIL
- Weighted score for PASS/CONDITIONAL candidates
- Key advantages
- Key disadvantages
- Hidden BOM / licensing impact
- Final recommendation and conditions

## Anti-patterns

Do not:

- Rank brands without project context.
- Compare a bare chassis against a fully configured system.
- Mix list price, tax-inclusive project price, and used-market price.
- Give high scores to unverified specifications.
- Average incompatible price evidence.
- Let a weighted score override a failed mandatory requirement.

## Exact configuration rule

For servers, compare CPU, CPU count, memory layout, drives, RAID/HBA, NIC, PSU, rails, warranty and software.

For switches, include optics/DAC, power supplies, stacking/MLAG features, licenses and support.

For firewalls, compare throughput under the required security services, subscriptions, HA licensing and support.

For UPS, compare kW, kVA, power factor, battery configuration, runtime target, bypass and service.

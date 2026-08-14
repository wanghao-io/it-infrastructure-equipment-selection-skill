# Governance

## Current state

The project currently has one person with repository and release authority. The operational bus factor is therefore **1**. This document does not claim otherwise: it defines how knowledge and authority can be distributed safely and how the status will be measured.

Current maintainers and vacancies are recorded in [MAINTAINERS.md](MAINTAINERS.md). Release operations are externalized in [docs/maintainer-release-runbook.md](docs/maintainer-release-runbook.md).

## Roles

### Contributor

Anyone who submits Issues, Discussions, reviews, documentation, tests, code, or verified domain evidence.

### Reviewer

A regular contributor trusted to triage Issues and review changes in one or more areas. Reviewers do not automatically receive write or release access.

### Maintainer

A reviewer with repository triage/write access who can merge changes after required checks pass. Maintainers are expected to protect contributor privacy, preserve vendor neutrality, and document decisions.

### Release maintainer

A maintainer who has demonstrated the release runbook in a non-destructive rehearsal and can create, verify, or recover a release. At least two active release maintainers are required before the project may report a release bus factor above 1.

## Promotion criteria

A contributor may be nominated by a maintainer or self-nominate in a public governance Issue after demonstrating:

- at least three substantive contributions or reviews across at least two releases;
- reliable use of tests and evidence, including correction of mistakes;
- familiarity with the contribution, security, and release processes;
- respectful participation under the Code of Conduct;
- no unresolved conflict-of-interest concern.

Promotion is recorded in a PR updating `MAINTAINERS.md`, with role scope and effective date. Write access is granted only after that PR merges. Release access additionally requires a witnessed rehearsal of the release runbook.

Inactive maintainers may move to Emeritus after six months without project activity or on request. Access that is no longer needed should be removed promptly.

## Decisions

Routine changes are decided through PR review and passing CI. Significant changes—schema compatibility, mandatory gates, security posture, governance, or release policy—must include an Issue or Discussion with alternatives and migration impact.

Seek rough consensus. When consensus is not possible, maintainers document the decision, objections, and reversible follow-up. A maintainer with a direct commercial conflict should recuse from the final decision when another qualified maintainer is available.

## Merge and release controls

- No release may be built from an unmerged commit.
- CI, release metadata, tag/version, archive, and checksum checks must pass.
- Force-pushing protected branches or moving published version tags is prohibited.
- Emergency fixes follow the same test and immutable-tag rules; urgency does not authorize rewriting a release.
- Secrets, signing keys, and personal credentials are never committed or shared through Issues.

## Bus-factor objective and measurement

The project may report bus factor 2 only when both conditions are true:

1. two active humans have repository write/maintain access; and
2. two active humans have independently completed a release rehearsal or real release verification within the previous six months.

Documentation, automation, and backups reduce recovery risk but do not by themselves change the human bus-factor count.

Quarterly, maintainers should review collaborator access, release capability, open security reports, stale triage, and the accuracy of `MAINTAINERS.md`.

## Succession and recovery

If the owner is unavailable, an existing release maintainer should:

1. verify repository and package integrity against the latest signed/annotated tag and published checksum;
2. follow the release runbook from a clean clone;
3. avoid rotating or sharing personal credentials through the repository;
4. record any temporary governance decision in a public Issue when safe;
5. update maintainer records and access only through auditable GitHub actions.

If no second maintainer exists, the project remains bus factor 1 and cannot claim a completed succession path. Community members may continue through forks and PRs while a qualified maintainer candidate is established.

# Security Policy

## Supported versions

Security fixes are applied to the latest release and `main`. Older releases may be used for comparison but are not maintained with backports unless a maintainer explicitly announces one.

## Report privately

Do not disclose a vulnerability, credential, confidential quotation, customer configuration, personal data, or sensitive network detail in a public Issue or Discussion.

Use GitHub's [private vulnerability reporting form](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/security/advisories/new). Include:

- affected version or commit;
- impact and realistic abuse scenario;
- minimal reproduction or affected file;
- whether sensitive project data may have been exposed;
- a safe contact method if GitHub notifications are insufficient.

If the report is about private conduct rather than a technical vulnerability, prefix the advisory title with `[Conduct]`; maintainers will route it under the Code of Conduct process.

## Response targets

- Acknowledge a complete report within 5 business days.
- Confirm severity and remediation plan within 10 business days when reproducible.
- Coordinate disclosure only after a fix or mitigation is available.
- Credit reporters unless they request anonymity.

Targets are service goals, not guarantees. The project currently has limited maintainer capacity; current ownership and vacancies are disclosed in [MAINTAINERS.md](MAINTAINERS.md).

## In scope

- installer behavior that can overwrite or execute unintended content;
- unsafe parsing, path handling, command construction, or supply-chain behavior;
- workflows that can expose credentials or publish unverified artifacts;
- deterministic gates that falsely mark unsafe infrastructure selections as eligible;
- accidental inclusion of confidential project data in repository artifacts.

General sizing disagreement, outdated price evidence, support questions, and feature requests belong in public Issues or Discussions unless they expose sensitive data.

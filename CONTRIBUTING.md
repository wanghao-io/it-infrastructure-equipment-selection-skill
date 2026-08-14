# Contributing

Thank you for helping make infrastructure selection safer, more reproducible, and easier to review. 中文贡献同样欢迎；Issue、Discussion 和 PR 可以使用中文或英文。

## Choose the right community channel

- Ask usage and design questions in [GitHub Discussions](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/discussions).
- Report reproducible defects with the [bug form](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/issues/new?template=bug.yml).
- Propose capabilities with the [feature form](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/issues/new?template=feature.yml).
- Report documentation gaps with the [documentation form](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/issues/new?template=documentation.yml).
- Report security or sensitive-data problems privately as described in [SECURITY.md](SECURITY.md).
- Read [SUPPORT.md](SUPPORT.md) when unsure where a request belongs.

Small documentation fixes may go directly to a pull request. For behavior, schema, or workflow changes, open an issue or Discussion first so the intended contract is clear.

## What to contribute

Useful contributions include:

- requirement discovery and architecture decision rules;
- server, storage, HCI, network, UPS, SCADA, IT/OT, and TCO methods;
- deterministic validators, calculators, and regression cases;
- current vendor-neutral specification or lifecycle evidence;
- price-evidence and RFQ normalization improvements;
- portability fixes for Codex, Claude Code, Copilot, Gemini CLI, and compatible hosts;
- documentation, examples, translations, and accessibility improvements.

Do not submit confidential project names, credentials, private quotations, network addresses, customer configurations, personal data, or material you cannot license to the project. Anonymize examples and use synthetic suppliers/prices in public tests.

## Development setup

The project uses the Python standard library for its deterministic tools.

```bash
git clone https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill.git
cd it-infrastructure-equipment-selection-skill
python3 -m compileall scripts tests
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate_release.py
```

Run the relevant workflow command as well, for example:

```bash
python3 scripts/compare_server_quotes.py assets/server-rfq-example.json --pretty
python3 scripts/calculate_hci_failover.py assets/hci-failover-example.json --pretty
```

## Engineering contribution rules

1. Preserve the order: requirements → architecture → sizing → technical eligibility → evidence quality → price.
2. Never let a cheaper product redefine a mandatory requirement.
3. Keep verified facts, assumptions, estimates, and unresolved items distinguishable.
4. Use deterministic scripts for fragile calculations or gates and add regression coverage.
5. Keep examples vendor-neutral unless a named product is required to demonstrate compatibility or lifecycle evidence.
6. Do not present live-price claims without dated, configuration-matched evidence.
7. Keep `SKILL.md` concise; place detailed domain guidance under `references/`.
8. Preserve cross-platform behavior and avoid host-specific requirements in the shared runtime.

## Pull requests

Create a focused branch and keep unrelated changes out of the same PR. Complete the pull request template, including:

- problem and root cause;
- behavior or documentation changed;
- user/developer impact;
- tests and deterministic commands run;
- compatibility, privacy, security, and release impact;
- before/after examples for output contract changes.

PRs must pass the full CI matrix. Maintainers may request a smaller change, additional tests, source evidence, or migration notes. Reviews should discuss the work, not the contributor, and follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Reviews and maintainer path

Anyone may review a PR. Useful reviews reproduce the behavior, identify an engineering risk, or suggest a concrete improvement.

Regular contributors can become reviewers or maintainers through the transparent criteria in [GOVERNANCE.md](GOVERNANCE.md). Current roles and vacancies are listed in [MAINTAINERS.md](MAINTAINERS.md). The goal is to distribute domain knowledge, triage, CI, and release capability instead of depending on one account.

## Release process

Only release maintainers create version tags. The repeatable process and recovery checks are documented in [docs/maintainer-release-runbook.md](docs/maintainer-release-runbook.md).

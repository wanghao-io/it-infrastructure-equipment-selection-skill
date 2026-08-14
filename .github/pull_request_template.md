## Problem

<!-- What problem or risk does this change address? Include the root cause for fixes. -->

## Change

<!-- Describe the focused change and any output/schema compatibility impact. -->

## Validation

- [ ] `python3 -m compileall scripts tests`
- [ ] `python3 -m unittest discover -s tests -p 'test_*.py' -v`
- [ ] `python3 scripts/validate_release.py`
- [ ] Relevant deterministic workflow command(s) run

Commands and results:

```text

```

## Safety and community checks

- [ ] No credentials, customer identities, private quotations, network addresses, or confidential configurations are included.
- [ ] Verified facts, assumptions, estimates, and TBD items remain distinguishable.
- [ ] Cheaper products do not redefine mandatory requirements.
- [ ] Documentation, examples, changelog, and release notes are updated when applicable.
- [ ] Cross-platform and installer impact has been considered.

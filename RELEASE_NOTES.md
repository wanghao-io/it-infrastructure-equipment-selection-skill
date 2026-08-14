# IT Infrastructure Equipment Selection Skill v1.4.3

## Release workflow Node 24 hotfix

v1.4.3 is a release-engineering-only hotfix. It updates the immutable GitHub Actions pins used to transfer verified release artifacts:

- `actions/upload-artifact` v7.0.1 on Node 24;
- `actions/download-artifact` v8.0.1 on Node 24.

This removes the Node 20 deprecation annotation observed during the v1.4.2 release run. A regression test now requires these exact Node 24 action commits and rejects the previous pins.

No Skill workflow, calculation formula, JSON Schema, compatibility contract, procurement rule, price-evidence gate or output profile changed. All v1.4.2 usability improvements, forward-validation findings and the proposed v1.5 scope remain in effect.

## Verification

- the complete local unit and scenario suite;
- JSON Schema catalog validation and release metadata consistency;
- Linux, macOS and Windows validation on Python 3.10 and 3.12;
- clean archive installation and deterministic smoke tests;
- staged `gh skill publish --dry-run` compatibility validation.

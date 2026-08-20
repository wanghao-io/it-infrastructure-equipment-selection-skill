# Maintainer Release Runbook

This runbook allows a qualified maintainer to reproduce a release from a clean clone without relying on undocumented local knowledge.

## Preconditions

- Work from a clean clone of the canonical repository.
- Confirm `gh auth status` and repository permission.
- Confirm the installed GitHub CLI exposes `gh skill publish --dry-run`; the Release workflow treats this preview capability as a hard compatibility gate.
- Confirm `main` matches `origin/main` and contains the intended PR merge.
- Never move or overwrite an existing version tag.
- Use a new semantic patch/minor/major version according to compatibility impact.

## Prepare the release PR

1. Update `VERSION`.
2. Add the matching `## vX.Y.Z` entry to `CHANGELOG.md`.
3. Replace `RELEASE_NOTES.md` with notes for **only** `Skill vX.Y.Z`; `CHANGELOG.md` remains the cumulative history.
4. Update README release-state text when applicable.
5. Run:

```bash
python3 -m compileall scripts tests
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate_release.py
python3 scripts/extract_release_notes.py "v$(cat VERSION)"
git diff --check
```

6. Push a focused branch, open a PR, and wait for every required GitHub Actions check.
7. Merge only the reviewed, unchanged PR head.

## Create a non-reused annotated release tag

The workflow refuses tag reuse and asset clobbering. GitHub's repository-level Immutable Releases setting is a separate governance control; do not claim `isImmutable=true` unless that setting has been enabled and verified.

From an updated clean `main`:

```bash
git fetch origin main --tags
git switch main
git pull --ff-only
test -z "$(git status --porcelain)"
VERSION_VALUE="$(cat VERSION)"
git ls-remote --exit-code --tags origin "refs/tags/v${VERSION_VALUE}" && exit 1 || true
git tag -a "v${VERSION_VALUE}" -m "IT Infrastructure Equipment Selection v${VERSION_VALUE}"
git push origin "v${VERSION_VALUE}"
```

The tag push triggers `.github/workflows/release.yml`. Do not create a second manual release while that workflow is running.

The workflow requires the tag SHA to remain the exact current `origin/main` head, calls the same full Linux/macOS/Windows validation used on `main`, validates a temporary standard `gh skill publish --dry-run` layout, builds from the tag, and smoke-tests a clean archive installation before its single write-enabled job creates the Release.

## Verify the release

```bash
gh run list --workflow Release --limit 3
gh run watch <run-id> --exit-status
gh release view "v$(cat VERSION)"
```

Verify:

- tag points to a commit reachable from `origin/main`;
- tag points to the exact current `origin/main` head;
- Release is neither draft nor prerelease unless intentionally documented;
- Release body contains only the current `CHANGELOG.md` version section;
- `skill.tar.gz` and `SHA256SUMS` exist;
- the archive checksum matches;
- a clean install/update reports the new version;
- at least one deterministic server quote and HCI smoke command runs from the installed copy.

## Failure and recovery

- If any validation or compatibility gate fails before a Release is published, fix through a new PR and create a new version tag. Do not move or reuse the failed tag.
- If a release artifact is incomplete or compromised, mark the release as affected, publish a new patch version, and document the reason in the changelog/security advisory as appropriate.
- If credentials may be exposed, revoke/rotate them outside the repository before discussing details publicly.
- Never use `git push --force` on `main` or a released tag.

## Rehearsal

A prospective release maintainer can satisfy the governance rehearsal requirement by performing all read-only validation and archive/checksum creation from a temporary clean clone, without pushing a tag. Record the rehearsal date and verifier in the maintainer promotion PR.

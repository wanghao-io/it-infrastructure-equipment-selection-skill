# Platform Compatibility

This project uses the portable core of the **Agent Skills** format: a skill directory with `SKILL.md`, YAML frontmatter, references, scripts and assets.

The goal is one skill codebase that can be installed into multiple agent hosts without maintaining separate copies of the engineering logic.

## Supported Hosts

| Host | Format / installer evidence | Discovery / scenario evidence | User-scope location | Project/workspace location |
|---|---|---|---|---|
| OpenAI Codex | CI copy-install plus staged `gh skill publish --dry-run` | verify `$it-infrastructure-equipment-selection` after install; fresh-agent records are simulated, not continuous host certification | `~/.agents/skills/<skill-name>/` | `.agents/skills/<skill-name>/` |
| Claude Code | path and copy-install compatibility tests | manual `/it-infrastructure-equipment-selection` scenario check required | `~/.claude/skills/<skill-name>/` | `.claude/skills/<skill-name>/` |
| GitHub Copilot | path and copy-install compatibility tests | manual discovery and matching-prompt check required | `~/.agents/skills/<skill-name>/` or `~/.copilot/skills/<skill-name>/` | `.github/skills/<skill-name>/`, `.agents/skills/<skill-name>/` or `.claude/skills/<skill-name>/` |
| Gemini CLI | path and copy-install compatibility tests | manual `/skills list`, reload and matching-prompt check required | `~/.agents/skills/<skill-name>/` or `~/.gemini/skills/<skill-name>/` | `.agents/skills/<skill-name>/` or `.gemini/skills/<skill-name>/` |
| Other Agent-Skills-compatible hosts | portable-format intent only | host-specific verification required | host-specific | host-specific |

`<skill-name>` is `it-infrastructure-equipment-selection`.

## Portability Rules

The portable runtime is based on:

- `SKILL.md`;
- `references/`;
- `scripts/`;
- `assets/`;
- `examples/`.

`agents/openai.yaml` is an **optional OpenAI/Codex extension**. It may provide OpenAI-specific UI metadata or behavior, but the engineering workflow must never depend on it. Other hosts should be able to use the skill from `SKILL.md` alone.

Keep the shared `SKILL.md` on the portable subset of the Agent Skills format:

- `name`;
- `description`;
- Markdown instructions and relative links to bundled resources.

The repository license remains in `LICENSE`; do not duplicate it as trigger metadata in the shared frontmatter.

Do not put Claude-Code-only, Codex-only, Copilot-only or Gemini-only behavior in the shared frontmatter unless there is a demonstrated cross-host need. Put host-specific installation/operation notes in this file instead.

## Runtime Capability Differences

Skill-format compatibility does **not** mean every host exposes the same tools.

This skill therefore uses capability-based behavior:

- If live web/search tools are available, current-price requests must use live research.
- If live research is unavailable, return `Needs confirmation` or an engineering estimate instead of presenting stale data as current price.
- If Python execution is available, deterministic calculators under `scripts/` should be used where relevant.
- If script execution is unavailable, follow the formulas/rules in the references and clearly state that the deterministic helper could not be run.
- Never assume a particular MCP server, browser, marketplace connector or shell permission exists unless the current host exposes it.

This keeps the skill useful across hosts without silently degrading evidence quality.

## CLI failure contract

`scripts/infra_cli.py` keeps Agent research separate from deterministic commands. Its guarded commands are `guide`, `server-quotes`, `price-evidence`, `migrate` and `project-check`.

- Exit `0` means the operation completed, not that every candidate or evidence claim passed. Inspect semantic status and per-candidate reasons; quote/price decisions can return a hold or needs-confirmation result successfully.
- Invalid contract/version, non-finite JSON and overwrite refusal exit non-zero. Project-check exits 0 for consistent records, 1 for FAIL or CONDITIONAL, and never certifies engineering truth.
- Machine output is written to stdout only after required preflight succeeds. Diagnostics go to stderr.
- Normal user errors are concise and contain no traceback; `--debug` may preserve a traceback.
- A failed migration or renderer must not overwrite the source or an existing destination.
- CLI success proves contract/calculation status only; it does not prove live price, lifecycle, technical truth or final engineering eligibility.

## Installer

Use the repository's portable installer:

```bash
python3 scripts/install_skill.py --target codex --scope user
python3 scripts/install_skill.py --target claude-code --scope user
python3 scripts/install_skill.py --target copilot --scope user
python3 scripts/install_skill.py --target gemini --scope user
```

For project/workspace scope:

```bash
python3 scripts/install_skill.py --target claude-code --scope project --project-dir /path/to/project
python3 scripts/install_skill.py --target copilot --scope project --project-dir /path/to/project
python3 scripts/install_skill.py --target gemini --scope project --project-dir /path/to/project
python3 scripts/install_skill.py --target codex --scope project --project-dir /path/to/project
```

The default installation mode is `copy`. For local development, use `--mode symlink` so edits in the cloned repository are picked up by the host:

```bash
python3 scripts/install_skill.py --target claude-code --scope user --mode symlink
```

Use `--force` only when intentionally replacing an existing installed copy.

Copy installs now record managed-file hashes in `.skill-install.json`. Updates validate a complete staged runtime, retain unrelated files and replace with rollback. Local managed edits stop normal updates. Legacy copies without a manifest require inspection and explicit `--force`; they are not silently adopted. A process/power loss can leave a sibling update directory containing `previous`; preserve it for recovery rather than deleting it blindly.

Git updates validate frontmatter identity and the origin against the explicitly supplied source checkout, or the official origin for self-update. For an intentionally trusted fork, supply `--trusted-origin`. Dirty checkouts remain protected and pulls remain fast-forward-only. This is source/identity checking, not cryptographic provenance or a guarantee about future upstream commits.

## Shared `.agents/skills` Strategy

Codex, GitHub Copilot and Gemini CLI can all use `.agents/skills` as a portable location. This makes a shared installation practical for those hosts.

Claude Code uses its own `.claude/skills` discovery location. If the same local skill repository should serve both Codex/Gemini/Copilot and Claude Code, install once under `~/.agents/skills/` and use a symlink under `~/.claude/skills/`, or use the installer separately for each host.

## Verification

After installation, verify discovery in the target host rather than assuming filesystem placement alone is sufficient.

Recommended checks:

- Codex: confirm the skill appears in skill discovery or explicitly invoke `$it-infrastructure-equipment-selection`.
- Claude Code: invoke `/it-infrastructure-equipment-selection` or ask a matching infrastructure-selection question.
- GitHub Copilot: verify the skill is discovered by the relevant Copilot agent/CLI and test a matching prompt.
- Gemini CLI: run `/skills list`; use `/skills reload` after adding or changing a skill if needed.

Then run at least one real scenario that exercises references and scripts, not only a discovery check.

## Compatibility Maintenance

Host discovery paths and optional extensions can evolve. When a host changes its Agent Skills implementation:

1. keep `SKILL.md` portable;
2. update only the host-specific installation guidance when possible;
3. add/adjust regression tests;
4. avoid forking the core engineering instructions into host-specific copies unless unavoidable.

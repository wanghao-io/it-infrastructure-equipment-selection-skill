# Platform Compatibility

This project uses the portable core of the **Agent Skills** format: a skill directory with `SKILL.md`, YAML frontmatter, references, scripts and assets.

The goal is one skill codebase that can be installed into multiple agent hosts without maintaining separate copies of the engineering logic.

## Supported Hosts

| Host | Status | User-scope location | Project/workspace location | Invocation / verification |
|---|---|---|---|---|
| OpenAI Codex | Supported | `~/.agents/skills/<skill-name>/` | `.agents/skills/<skill-name>/` | invoke with `$it-infrastructure-equipment-selection` or let Codex select it |
| Claude Code | Supported | `~/.claude/skills/<skill-name>/` | `.claude/skills/<skill-name>/` | invoke with `/it-infrastructure-equipment-selection` or let Claude select it |
| GitHub Copilot | Supported | `~/.agents/skills/<skill-name>/` or `~/.copilot/skills/<skill-name>/` | `.github/skills/<skill-name>/`, `.agents/skills/<skill-name>/` or `.claude/skills/<skill-name>/` | Copilot selects relevant skills; Copilot CLI can inspect/reload skills |
| Gemini CLI | Supported | `~/.agents/skills/<skill-name>/` or `~/.gemini/skills/<skill-name>/` | `.agents/skills/<skill-name>/` or `.gemini/skills/<skill-name>/` | use `/skills list` / `/skills reload`; Gemini activates matching skills |
| Other Agent-Skills-compatible hosts | Format-compatible | host-specific | host-specific | follow the host's current skill-discovery documentation |

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
- `license`;
- Markdown instructions and relative links to bundled resources.

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

## Installer

Use the repository's portable installer:

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

For project/workspace scope:

```bash
python scripts/install_skill.py --target claude-code --scope project --project-dir /path/to/project
python scripts/install_skill.py --target copilot --scope project --project-dir /path/to/project
python scripts/install_skill.py --target gemini --scope project --project-dir /path/to/project
python scripts/install_skill.py --target codex --scope project --project-dir /path/to/project
```

The default installation mode is `copy`. For local development, use `--mode symlink` so edits in the cloned repository are picked up by the host:

```bash
python scripts/install_skill.py --target claude-code --scope user --mode symlink
```

Use `--force` only when intentionally replacing an existing installed copy.

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

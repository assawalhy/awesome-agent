# Support the Pi coding agent harness

## Goal
Add `pi` (the minimal extensible agent harness, `~/.pi/agent`) as a supported install
target so `/todo`, `/continue`, `/epic`, `/go` and the `awesome-plan` skill install and
work for Pi users, next to the existing opencode/claude/codex/... harnesses.

## Approach
- Add a `pi` harness entry to install.sh: target root `~/.pi/agent`, command dir
  `prompts` (Pi prompt templates, invoked `/name`), skill root `skills`, no md agents.
- Add `pi` to `harness_installed` (detect `command -v pi`), `harness_label`,
  `ALL_IDS`, and the `usage()` help.
- Add `harnesses/pi/.skip` listing `agents/awesome-agent.md` — Pi has no file-based
  markdown subagents (its "What we didn't build" section lists no sub-agents; you build
  or install them as extensions).
- Shared files install as-is, no per-harness content overlay needed:
  - `commands/*.md` are valid Pi prompt templates: `description` frontmatter is read by
    Pi's autocomplete, and body prose uses `$ARGUMENTS` which Pi expands in templates.
  - `skills/awesome-plan/SKILL.md` installs into `~/.pi/agent/skills/awesome-plan/`
    and is discovered recursively (a dir containing SKILL.md); its frontmatter already
    has the required `name` + `description`.
- No default-agent step for pi (that is opencode-specific).
- Mirror pi in `local_dirs()` (`~/.pi` project dir detection) for consistency with the
  other mirrored harnesses.
- Update README (What you get list, file layout, limitations), MANIFEST comment if needed,
  and bump VERSION (0.2.0 -> 0.3.0, minor: a new supported harness).

## Decisions
- Prompt templates instead of slash commands: Pi does not have user-defined slash
  commands; its analog is prompt templates in `~/.pi/agent/prompts/`, invoked as
  `/todo`, `/continue`, `/epic`, `/go`. Mapped reusing the codex `commands -> prompts/`
  directory-table pattern.
- No content overlay for command files: their `description` frontmatter + `$ARGUMENTS`
  body is already Pi-compatible (verified in Pi's prompt-templates.md + skills.md docs).
- `agents/awesome-agent.md` skipped via `.skip`, same mechanism as codex: Pi has no
  markdown-subagent concept. Rejected building a subagent extension: out of scope and
  the plugin's value for pi is commands + the skill, matching what every other harness
  gets.
- VERSION 0.3.0 (minor) because this is a new feature/harness, consistent with the
  previous minor bump when per-harness support grew (0.2.0).

## Milestones
- M1: install.sh `pi` harness entry (dirs, detect, label, ALL_IDS, usage, local_dirs)
- M2: harnesses/pi/.skip + README + VERSION 0.3.0
- M3: fake-HOME install/update/uninstall test green for `pi`

## Risks
- `command -v pi` could false-positive if an unrelated `pi` binary exists on PATH; the
  installer's detect-then-multi-select flow already lets users deselect, so this is a
  minor risk (same as other harnesses).
- Pi layout is evolving fast (v0.84.x); `~/.pi/agent/prompts/` and `skills/` are the
  documented stable globals, so this should be OK; note it in README limitations.
- Pi skill name must be lowercase/hyphens — `awesome-plan` is valid.

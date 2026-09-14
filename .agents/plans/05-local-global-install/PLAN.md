# Choose global vs project-local install per harness

> Status: **COMPLETE** — M1–M4 done, all TODO items `[x]`, fake-HOME/temp-project
> matrix + interactive TUI checks green.

## Goal
Today `install.sh` hardwires where a harness's files go: every harness installs
user/global under `$HOME`, except `cursor` (always `$PWD/.cursor`) and the `local`
pseudo-target. Make scope a user choice — **global** (default) or **project-local** —
for every harness that documents a project-level directory, so the same plugin can be
installed to a repo instead of (or in addition to) the user's home.

## Research (resolved before approval; see Decisions)
Project-level support, per official docs:
- Full project support (commands + agents + skills): **opencode** `.opencode/`,
  **claude** `.claude/`, **cursor** `.cursor/`, **pi** `.pi/` (prompts+skills),
  **kilo** `.kilo/`, **kiro** `.kiro/`.
- Global-only / partial: **codex** prompts are global-only (`.codex/prompts/`; OpenAI
  closed the project-prompt request as not planned) though skills are project-capable;
  **kimi** has no user command dir (commands are skills); **deepseek** is a niche
  third-party CLI (no documented command/agent dirs).
- **Cursor supports `~/.cursor/` globally** — the current forced `$PWD/.cursor` is a bug.

## Approach
- `harness_dirs <id> <scope>` splits into `harness_dirs_global` (current table, cursor
  fixed to `$HOME/.cursor`) and `harness_dirs_local` (project table:
  `.opencode/.claude/.cursor/.pi/.kilo/.kiro`). `harness_scopes <id>` declares
  `global local` vs `global`; `local` target stays scope `local`.
- Registry keys become `id:scope` (`opencode:global`, `claude:local`, `local:local`).
  A one-time `migrate_registry` rewrites bare legacy keys: `cursor`/`local` → `:local`,
  else `:global`.
- Interactive flow: existing target multi-select, then a second multi-select of
  `"<harness> — global"` / `"<harness> — project"` rows (globals pre-selected; picking
  both installs both). Harnesses without local support install global silently.
- Non-interactive: new `--scope global|local|both` (default global) plus per-target
  `id:scope` (`--target claude:local,opencode`). `--all` stays global; `--all --scope both`
  installs both where supported.
- opencode's `default_agent` edit is global-only (project opencode config lives at the
  repo root `opencode.json`, not under `.opencode/`), so `opencode:local` skips it.
- `local` target and `local_dirs()` retained unchanged for backward compatibility.
- Docs: README (install/update/uninstall + decision rationale + limitations), usage()
  help, VERSION 0.3.0 → 0.4.0. MANIFEST untouched.

## Decisions
- **Second multi-select for scope, not per-harness entries**: keeps the harness list
  stable and lets "both" fall out naturally (select both rows). Rejected doubling every
  list row (noisy, `--all` semantics ambiguous) and flag-only (no discoverability).
- **Scope only where documented**: opencode/claude/cursor/pi/kilo/kiro get the choice;
  codex/kimi/deepseek are global-only with a printed reason. Rejected partial local
  installs (skills local + prompts global) because one harness split across two roots
  complicates the registry and uninstall for little gain.
- **Default global**: matches today's behavior for every harness but cursor, so no
  surprise re-homing on plain `./install.sh` / `--all`.
- **Cursor default flips to global**: consistency with all other harnesses; local still
  selectable. This is an intentional behavior change for cursor.
- **Registry `id:scope`, migrated once**: the only way a harness can be installed in
  both scopes without one clobbering the other. Rejected a separate registry file
  (two sources of truth).
- **Pure bash, no new deps**: reuses the existing TUI and overlay/.skip machinery from
  epics 02/04.

## Milestones
- M1: scope-aware `harness_dirs`/`harness_scopes` + `id:scope` registry + migration
- M2: interactive scope multi-select + `--scope` / `id:scope` CLI
- M3: cursor global default, opencode default global-only, README + usage + VERSION 0.4.0
- M4: fake-HOME/temp-project test matrix green (install/update/uninstall, both scopes,
  migration, global-only harnesses)

## Risks
- Behavior change: existing cursor installs register as `cursor:local`; `update` keeps
  them local until the user explicitly installs global. Documented.
- Registry migration is destructive (rewrites keys); guarded to run only when a bare key
  exists, and reversible by the same rule.
- Pre-existing kiro/opencode subdir naming quirks are mirrored (global table is the
  source of truth for local subdirs); not fixed here.

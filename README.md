# awesome-agent

> Drop-in plugin that brings plan-first, human-supervisable, traceable, and parallel
> agentic coding to many AI harnesses.

`awesome-agent` installs four slash commands, two custom agents, and three skills into any
supported AI coding harness (OpenCode, Claude Code, Codex, Pi, Kilo, Kiro, Kimi,
DeepSeek, Cursor, or your current project folder) — **globally** (under your home
directory) or **project-locally** (into the repo you run it from), your choice.

## The problem and the solution

**I faced some issues when I work in a project where I run multiple agents to do different tasks or goals like:**
- they conflict with each other
- lose track of one's tasks and progress
- can't handoff the work to another agent ot continue
- can't know which one is working on what
- don't have a record and history track of the dicision and trade-offs
- the agent skip planning sometime
- in OpenCode it is not direct to switch from Plan agent to Build agent
- the plan is hard to read and is itself a puzzle to solve
- the parallel agent runs multiple heavy tasks for e2e tests and build on my average machine that frozes and crashes

**The solution of all of these issues is basically these simple fixes:**
- track your plans and TODO list in .md files grouped together in epics
- use the same agent (mode) for planning and executing
- general instruction for the agent to research and get your opnion about the tradoffs and grilling you
- tell the agent to show the plan in a human-readable way
- use a single heavy tasks queue for all your agents and harnesses in your machine

## What you get

| Piece | File | Purpose |
| --- | --- | --- |
| `/todo` | `commands/todo.md` | Add a task to the active epic it belongs to (ask if none fits), then start it after current WIP |
| `/continue` | `commands/continue.md` | Resume unfinished work, report sub-agents / background jobs |
| `/epic` | `commands/epic.md` | Plan a big feature/epic (awesome-plan) then build |
| `/go` | `commands/go.md` | Auto-execute the active plan; manual fallback if none |
| `awesome-agent` | `agents/awesome-agent.md` | Plan-first agent you can delegate to |
| `awesome-worker` | `agents/awesome-worker.md` | Cheap-model sub-agent: executes a given spec, reports a terse verified result |
| `awesome-plan` | `skills/awesome-plan/SKILL.md` | The plan → approve → execute workflow the agent follows |
| `pr-description` | `skills/pr-description/SKILL.md` | Write a PR description for the current branch — product or technical style |
| `ddd` | `skills/ddd/SKILL.md` | Domain-Driven Design + Clean Architecture layering — detects the repo's own topology (CQRS split, command-only, unsplit, flat) and conforms to it |

Plans and TODOs are stored under `.agents/plans/<NN>-<slug>/` (see your existing
`~/.agents/AGENTS.md` convention), so the plugin slots into the workflow you already use.

Installing into OpenCode also sets `awesome-agent` as the default agent
(`"default_agent": "awesome-agent"` in `~/.config/opencode/opencode.json`), so new
sessions start with the plan-first workflow instead of opencode's built-in `build`.
Uninstall restores your previous default, or removes the setting so opencode falls
back to `build`. (Only for the global scope — project installs never touch your
personal OpenCode config.)

## Install / update / uninstall

```bash
./install.sh            # detect harnesses, pick targets, then pick scope (TUI)
./install.sh --all      # every detected harness, global scope
./install.sh --target opencode,claude
./install.sh update     # re-copy current files + prune removed ones
./install.sh uninstall  # remove from registered targets, including legacy files
```

### Scope: global vs project

Each install target has a **scope**:

- `global` (default) — the harness's user directory under `$HOME`
  (`~/.claude`, `~/.cursor`, `~/.config/opencode`, …).
- `local` — the project directory of the repo you run `./install.sh` from
  (`.claude/`, `.cursor/`, `.opencode/`, …), so the plugin travels with the repo.

Interactively, after selecting harnesses you get a second prompt with a row per
harness: pick `global`, `project`, or both. Non-interactively use `--scope`
and/or a per-target `id:scope`:

```bash
./install.sh --target claude:local,opencode    # claude in this project, opencode global
./install.sh --target claude:local,claude:global   # both
./install.sh --all --scope both                # both scopes, where supported
```

Local scope is offered for **opencode, claude, cursor, pi, kilo and kiro** (their
project directories are documented). **codex, kimi and deepseek are global-only** —
`codex` custom prompts have no project directory, `kimi` has no user command
directory, and `deepseek`'s layout is a thin third-party one; a local request for
them falls back to global (an explicit `codex:local` is rejected). A harness can be
installed in both scopes at once; they are tracked separately (`claude:global`,
`claude:local`) and uninstall only the scope you pick.

`cursor` now **defaults to global** (`~/.cursor`), like every other harness; project
installs are opt-in with `--scope local` or `cursor:local`. (Earlier versions always
installed cursor into `$PWD/.cursor`; those existing installs are registered as
`cursor:local` and keep updating/uninstalling there until you explicitly install global.)

Installing into OpenCode (`--target opencode`) also writes
`"default_agent": "awesome-agent"` into `~/.config/opencode/opencode.json` (or
`.jsonc`); uninstall restores the previous value (or removes the key) so the config
stays valid and opencode falls back to its built-in default agent. This applies to
the global scope only.

## Auto mode: let the skill own the gate, not the harness

Most harnesses ship a *plan mode* — a separate mode or agent that is allowed to read but
not write, which you then manually switch out of to execute. `awesome-agent` deliberately
does not use it. The `awesome-plan` skill already owns the whole
**research → plan → approve → execute → track** loop, including the hard approval gate, so
a harness-level mode switch adds a second gate that does the same job worse:

- the mode boundary is not the *plan* boundary — you can exit plan mode with no plan
  written, or be stuck in it with an approved plan you can't act on;
- switching modes usually starts a fresh context, so the reasoning behind the plan is lost
  exactly when execution needs it (this is the opencode Plan → Build friction the plugin
  was written for);
- the artifact disappears. A harness plan mode leaves you a transcript; `awesome-plan`
  leaves `PLAN.md` + `TODO.md` on disk, reviewable in a PR.

**So: run the harness wide open, and let the skill stop you.** One agent, one context,
plans and executes; the gate is the `go` reply, and the record is the files.

| Harness | How to run it |
| --- | --- |
| Claude Code | Auto mode (`shift+tab` to cycle, or `/config` → permission mode). Invoke `/awesome-plan`, `/epic`, or `/todo`; the skill gates execution, so auto-accept is safe. Don't use `/plan`. |
| OpenCode | Install sets `default_agent: awesome-agent`, so new sessions already start plan-first. Stay on it — don't switch to `plan` or `build`. |
| Cursor | Pick the `awesome-agent` agent, then Auto/Agent mode rather than Ask/Plan. |
| Codex / Pi | No file-based agents: run the prompts (`/prompts:epic`, `/todo`, …) with approvals set to auto/full-access. The skill still gates the write phase. |
| Kilo / Kiro / Kimi / DeepSeek | Select the `awesome-agent` agent (Kiro install also sets `chat.defaultAgent`) and use their autonomous/auto-approve mode, not a built-in plan mode. |

If you'd rather not remember this per harness, put it in your global instructions —
`~/.agents/AGENTS.md` or the harness's equivalent — so every agent picks it up:

```markdown
## Planning

Run in auto mode. Don't use the harness's plan mode or a separate planning agent —
the `awesome-plan` skill owns the plan → approve → execute gate. One agent plans and
executes in one context; the approval gate is the user's `go` reply, and the record is
`PLAN.md` + `TODO.md` under `.agents/plans/<NN>-<slug>/`.
```

## Design rationale (why it works the way it does)

### 1. Plan-first with a hard approval gate
The agent never writes code before a plan exists, and it stops after drafting to ask
`go` / refine. This is deliberate: agentic coding fails most often by *committing* to a
wrong direction before a human can intervene. A cheap plan + a one-line question costs
almost nothing and prevents large wasted diffs. The approval gate is a single choke point
the user controls; everything downstream (execution, orchestration, new sessions) only
runs after it.

### 2. Human-supervisable artifacts
PLAN.md and TODO.md are plain Markdown a person can read in a normal editor or a PR. The
agent is not the source of truth — the files are. This keeps a human "in the loop" without
forcing them to read agent transcripts, and it makes the work reviewable after the fact.
TODO.md is updated live: each item is marked `[x]` the moment it is finished and verified,
so the visible checklist always reflects real progress instead of being rewritten all at
once at the end.

### 3. Why a separate agent + skill instead of only slash commands
The slash commands (`/todo` … `/go`) are for *you* to drive the agent interactively from
the main session. The `awesome-agent` agent is for *delegation*: you hand it a goal and it
runs the same workflow autonomously. Splitting the workflow into the `awesome-plan` skill
means the rules live in one place and are shared by both the slash commands (via `/epic`)
and the agent, so they cannot drift apart.

### 4. Worktree orchestration
Independent TODO items are executed on separate git worktrees, each driven by its own
sub-agent. Rationale: parallel agents sharing one working tree step on each other (file
conflicts, half-written states). Worktrees give isolation + a clean merge boundary, so
failures stay contained and the main tree is never left broken. Merging happens only after
every sub-agent reports done.

### 5. New-session delegation
Execution is handed to a fresh sub-agent so the supervising session stays free to review,
approve, or redirect. This avoids the "context fill" problem where a long autonomous run
forgets earlier instructions — the orchestrator keeps the overview, workers do the detail.

### 6. Multi-harness, drop-in
Different harnesses store slash commands / agents / skills in different directories. The
installer detects which harnesses are present and copies each file into that harness's
native directory, so one plugin works across OpenCode, Claude Code, etc. without per-tool
packaging. Command files use Claude-style frontmatter (`description` + `$ARGUMENTS`),
which OpenCode, Claude Code and Kilo all accept.

### 6b. Per-harness files, base + overlays
Harness nuances are covered by *files*, not bash rendering logic. `commands/`, `agents/`
and `skills/` are the shared base; `harnesses/<id>/` holds files that differ per harness
(we follow the base + per-harness overlays pattern used by Kustomize/ArgoCD and the
wshobson/agents multi-harness plugin marketplace). Resolution at install time:
a harness-specific file wins over the shared base, and `harnesses/<id>/.skip` lists
shared files *not* installed for that harness (e.g. codex has no markdown agents).
Files that only differ in install *location* (codex commands → `prompts/`) stay a
directory mapping. This keeps `./install.sh` a single command with no build step, and
harness quirks stay visible and reviewable as plain files.

### 7. MANIFEST-based tracking (safe uninstall of removed files)
`MANIFEST.txt` records every shipped file as
`repo-relative-path | version_added | version_removed` (`-` while live). The installer keeps
a per-target registry of *what it installed*, not just what currently ships. Therefore when
a command or skill is later removed from the plugin (set `version_removed` to its drop
version), both `update` and `uninstall` still delete that file from every target it was ever
installed to — even though it no longer exists in the repo. This prevents orphan files
accumulating in your harness configs over time.

### 8. Pure-bash TUI, no dependencies
The multi-select installer uses only POSIX-ish bash + `tput` so it runs anywhere (the user's
machine is zsh/bash) with no `gum`/`fzf` requirement.

### 9. Balance gate: plan when it pays, act when it doesn't
Planning + an approval round-trip costs a turn. For trivial work (a one-line fix) or when the
user already handed you the plan, that overhead is pure waste — so the agent skips straight to
execution. For anything non-trivial without a given plan, it still plans first and waits for
`go`. This keeps the guardrail where it matters without adding friction to small tasks.

### 10. Route work to the right epic, and ask when it doesn't fit
Tasks land in an *active* epic (one with open TODO items) whose PLAN.md goal matches the
task. Several candidates → ask. No active epic fits → ask whether to create a new one. This
prevents the plans directory from accumulating orphaned or mislabeled work, and keeps a human
in control of epic boundaries.

### 11. Skills detect the repo instead of imposing a canon
The `ddd` skill was originally one employer-specific document that asserted every bounded
context splits into `command/` + `query/` before anything else. Surveying real services
showed four topologies in production — CQRS split, command-only, unsplit layered, and no
contexts at all — two of them inside the *same* service. So the skill now leads with a
detection step and treats the command/query split as an optional per-context overlay on
top of the one real invariant, layering.

That creates the harder problem the skill actually solves: **when does the repo's existing
pattern win over the canon?** It sorts every difference into three buckets — *variation*
(arbitrary choice, no correctness consequence → conform silently), *defect* (an invariant
is broken → write new code correctly, name it once, don't refactor uninvited), and *typo*
(just wrong → don't copy it forward). Two rules keep that decidable: frequency decides
(a one-off is an accident, a service-wide deviation *is* that service's convention), and
correctness of new code outranks local consistency, which outranks the document. Structural
improvements are proposed, never bundled into a feature change.

The split canon and the Kotlin/Spring mechanics live in `skills/ddd/references/` and are
loaded only when relevant, so the always-loaded `SKILL.md` stays cheap on every prompt.
### 12. Scope is a user choice, not a per-harness accident
Whether a harness's files are personal (`~/.claude`) or travel with a repo (`.claude/`) is a
property of *how you work*, not of the tool — so every harness that documents a project
directory gets the choice, defaulting to the old global behavior. Only harnesses with a real
project directory are offered it (no made-up `.codex/`): a request for local scope on a
global-only harness falls back to global rather than scattering files somewhere the harness
never reads. The registry keys targets by `id:scope` so one harness can live in both places
without uninstall ambiguity, and pre-scope registries migrate once (old `cursor`/`local`
entries were project installs, everything else global).

### 13. Long work is delegated, and the model matches the work
A long-running TODO item grinds the coordinator's context and blocks supervision, so it goes
to a background sub-agent instead — and the sub-agent's model is chosen by reasoning weight:
mechanical, spec-following items that only need to report a result go to `awesome-worker` on a
fast/cheap model, while reasoning-heavy items keep the parent's own (heavy) model. Cursor's
worker ships as `model: fast`, Claude's as `model: haiku` (harness keywords, not hardcoded
provider models); in OpenCode the Task tool can't pick a model per call, so the worker file
carries a commented `model:` line — uncomment it with any cheap `provider/model` you have.
The coordinator always validates a worker's result before ticking `- [x]`.

## File layout

```
awesome-agent/
  install.sh            # detector + TUI + scope selection + install/update/uninstall
  VERSION               # plugin version
  MANIFEST.txt          # tracked files (added/removed versions)
  commands/             # slash commands: todo, continue, epic, go (shared base)
  agents/               # awesome-agent (plan-first) + awesome-worker (cheap executor) — shared, opencode-native
  skills/               # awesome-plan (the workflow skill), pr-description, ddd — shared base
    ddd/                # SKILL.md + references/{cqrs,kotlin-spring}.md (loaded on demand)
  harnesses/            # per-harness overlays (files that differ per harness)
    claude/agents/awesome-agent.md   # tools: frontmatter variant for Claude Code
    claude/agents/awesome-worker.md  # model: haiku worker
    cursor/agents/awesome-agent.md   # tools: frontmatter variant for Cursor
    cursor/agents/awesome-worker.md  # model: fast worker
    codex/.skip                      # agent files (codex has no md agents)
    pi/.skip                         # agent files (pi has no md agents)
```

Install roots are resolved per harness *and scope*: global roots live under `$HOME`
(`~/.claude`, `~/.cursor`, `~/.config/opencode`, `~/.pi/agent`, …), local roots are the
project directories (`.claude/`, `.cursor/`, `.opencode/`, `.pi/`, `.kilo/`, `.kiro/`).

## Limitations

- Verified directory mappings: opencode, claude, codex, pi, kilo, cursor. `kiro`, `kimi` and
  `deepseek` use best-effort layouts (their public docs are thin) — verify per harness.
- Project-local scope exists only for opencode, claude, cursor, pi, kilo and kiro. Codex,
  Kimi and DeepSeek are global-only (no documented project command/agent directory), and a
  `--scope local` request for them installs globally instead.
- Codex has no user-defined slash commands or file-based agents: commands install into
  `~/.codex/prompts/` (invoked as `/prompts:todo`, …), the agent file is skipped via
  `harnesses/codex/.skip`, and the skill installs into `~/.codex/skills/`.
- Pi likewise has no user-defined slash commands or file-based agents: commands install into
  `~/.pi/agent/prompts/` as prompt templates (invoked as `/todo`, …), the agent file is skipped
  via `harnesses/pi/.skip`, and the skill installs into `~/.pi/agent/skills/`. Pi's layout is
  evolving fast (v0.84.x); these are its documented stable globals.
- Claude/Cursor agents are rendered with their `tools:`-list frontmatter; the body is shared.
  The Cursor worker pins `model: fast` and the Claude worker `model: haiku` — harness-level
  keywords whose concrete model you control in each tool's own settings. Elsewhere (opencode,
  kilo, …) the worker inherits the parent model until you uncomment its `model:` line.
- `grill-me` has `disable-model-invocation`, so `/epic` uses awesome-plan's built-in interview
  (self-contained) instead of auto-triggering the external skill.

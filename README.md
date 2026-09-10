# awesome-agent

> Drop-in plugin that brings plan-first, human-supervisable, traceable, and parallel
> agentic coding to many AI harnesses.

`awesome-agent` installs four slash commands, one custom agent, and one skill into any
supported AI coding harness (OpenCode, Claude Code, Codex, Pi, Kilo, Kiro, Kimi,
DeepSeek, Cursor, or your current project folder).

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
| `awesome-plan` | `skills/awesome-plan/SKILL.md` | The plan → approve → execute workflow the agent follows |
| `pr-description` | `skills/pr-description/SKILL.md` | Write a PR description for the current branch — product or technical style |

Plans and TODOs are stored under `.agents/plans/<NN>-<slug>/` (see your existing
`~/.agents/AGENTS.md` convention), so the plugin slots into the workflow you already use.

Installing into OpenCode also sets `awesome-agent` as the default agent
(`"default_agent": "awesome-agent"` in `~/.config/opencode/opencode.json`), so new
sessions start with the plan-first workflow instead of opencode's built-in `build`.
Uninstall restores your previous default, or removes the setting so opencode falls
back to `build`.

## Install / update / uninstall

```bash
./install.sh            # detect harnesses, multi-select targets (TUI)
./install.sh --all      # every detected harness
./install.sh --target opencode,claude
./install.sh update     # re-copy current files + prune removed ones
./install.sh uninstall  # remove from registered targets, including legacy files
```

Installing into OpenCode (`--target opencode`) also writes
`"default_agent": "awesome-agent"` into `~/.config/opencode/opencode.json` (or
`.jsonc`); uninstall restores the previous value (or removes the key) so the config
stays valid and opencode falls back to its built-in default agent.

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

## File layout

```
awesome-agent/
  install.sh            # detector + TUI + install/update/uninstall
  VERSION               # plugin version
  MANIFEST.txt          # tracked files (added/removed versions)
  commands/             # slash commands: todo, continue, epic, go (shared base)
  agents/               # awesome-agent (plan-first agent) — shared, opencode-native
  skills/               # awesome-plan (the workflow skill), pr-description — shared base
  harnesses/            # per-harness overlays (files that differ per harness)
    claude/agents/awesome-agent.md   # tools: frontmatter variant for Claude Code
    cursor/agents/awesome-agent.md   # tools: frontmatter variant for Cursor
    codex/.skip                      # agents/awesome-agent.md (codex has no md agents)
    pi/.skip                         # agents/awesome-agent.md (pi has no md agents)
```

## Limitations

- Verified directory mappings: opencode, claude, codex, pi, kilo, cursor. `kiro`, `kimi` and
  `deepseek` use best-effort layouts (their public docs are thin) — verify per harness.
- Codex has no user-defined slash commands or file-based agents: commands install into
  `~/.codex/prompts/` (invoked as `/prompts:todo`, …), the agent file is skipped via
  `harnesses/codex/.skip`, and the skill installs into `~/.codex/skills/`.
- Pi likewise has no user-defined slash commands or file-based agents: commands install into
  `~/.pi/agent/prompts/` as prompt templates (invoked as `/todo`, …), the agent file is skipped
  via `harnesses/pi/.skip`, and the skill installs into `~/.pi/agent/skills/`. Pi's layout is
  evolving fast (v0.84.x); these are its documented stable globals.
- Claude/Cursor agents are rendered with their `tools:`-list frontmatter; the body is shared.
- `grill-me` has `disable-model-invocation`, so `/epic` uses awesome-plan's built-in interview
  (self-contained) instead of auto-triggering the external skill.

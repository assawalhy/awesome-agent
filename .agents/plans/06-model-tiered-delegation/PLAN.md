# Model-tiered sub-agent delegation

## Goal

For long-running TODO items, awesome-agent delegates to sub-agents instead of
blocking its own session — and picks the model by work weight: a fast/cheap
worker for mechanical items that just execute a spec and report back; the
parent's own (heavy) model for reasoning-heavy items.

## Approach

Add a second shipped sub-agent, `awesome-worker` — a "dumb muscle" persona:
follow the given spec exactly, never re-plan, return result + minimal
reasoning. Its model is set per harness via frontmatter overlays. Teach the
skill + agent rules to classify each delegated TODO item as light (worker) or
heavy (same-tier agent) and to launch long work in the background.

Model control per harness (verified in docs):
- Cursor: subagent frontmatter `model: fast` (built-in fast-model keyword) — overlay.
- Claude: subagent frontmatter `model: haiku` (alias) — overlay.
- OpenCode: no per-call model on the Task tool; child inherits parent when
  `model:` is unset. Shared base ships an inheritance default + a commented
  `model:` line so users pin their own cheap model.
- codex / pi: agent files skipped via existing `.skip` (unchanged behavior).

## Decisions

- Separate worker agent file, not prompt-only guidance — harnesses resolve the
  subagent's model from its frontmatter; opencode's Task tool has no per-call
  model arg. Rejected: "spawn on a cheap model" instruction alone — unactionable
  in native opencode/cursor.
- `model: fast` (Cursor) and `model: haiku` (Claude) keywords; rejected hardcoding
  a provider model id everywhere — breaks portability across users/providers.
- Heavy tier = inherit the parent model; rejected a second "smart worker" file —
  inherits already are the parent's model, duplication adds drift.
- Worker contract in its prompt: implement + verify + report terse result; no
  plan changes, no scope creep — the coordinator stays the brain.
- Long-running item → background sub-agent on a worktree (extends existing
  rule 8), so the main session keeps supervising; heavy-reasoning items may also
  go to background workers but on the same-tier model.
- VERSION 0.4.0 → 0.6.0 (0.5.0 was taken by upstream ddd release); manifest entry
  `agents/awesome-worker.md|0.6.0|-`.

## Milestones

- M1: worker agent file (shared base) + cursor/claude overlays + manifest/VERSION.
- M2: SKILL.md workflow + agent core rules (shared + overlays) teach tiering.
- M3: README docs; temp-HOME install test (correct file lands per harness,
  codex/pi skip); `./install.sh update` to sync all registered targets.

## Risks

- Shared-base worker has no cheap model by default in opencode/kilo/kiro/… —
  inherits parent (heavy) until the user edits one line; documented.
- Cursor's `fast` routes to whatever the user configured in settings; Claude's
  `haiku` alias could change upstream — both are the documented stable knobs.
- Unknown frontmatter keys on less-documented harnesses are ignored, not errors.

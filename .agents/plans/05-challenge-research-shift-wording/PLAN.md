# Make awesome-agent challenge the user, research, and ask before shifting the ask

## Goal
Update the wording in the awesome-agent agent files, the awesome-plan skill,
and their per-harness copies so the agent:
1. Challenges the user's idea (respectfully pushes back instead of agreeing).
2. Does the research instead of being lazy / asking questions it can answer itself.
3. When preparing a plan, if the plan would shift from the original ask
   (tradeoff or scope change), names that shift and asks for confirmation
   before proceeding.
4. Updates TODO.md item-by-item as it finishes and verifies each task — marks
   `[x]` immediately, never batches status updates at the end.

## Approach
Edit these source files (shared base has a `challenge` canonical wording; each
harness gets the same ideas phrased in its own voice):

- `skills/awesome-plan/SKILL.md` — extend Concepts + Research step.
- `agents/awesome-agent.md` — extend the non-negotiables list.
- `harnesses/claude/agents/awesome-agent.md`, `harnesses/cursor/agents/awesome-agent.md` —
  extend Core rules.
- `harnesses/kiro/agents/awesome-agent.md` + `.json` — extend the prompt body.
- `commands/epic.md` — extend the interview step.
- README.md — note the challenge/research behavior.

Then copy the changed shared files into `.awesome-agent/` (the repo-local mirror
layout used when the repo itself is the target) and reinstall to all harnesses
on this machine (opencode, claude, kiro, cursor if present) so installed copies
carry the new wording.

## Decisions
- Wording lives in the 6 source files; `.awesome-agent/` copies and every
  installed copy under `~/.config/opencode`, `~/.claude`, `~/.cursor`,
  `~/.kiro` are derived and must be refreshed by copying + `install.sh`,
  never hand-edited.
- Rejected: only editing the skill (agent files must carry the behavior too —
  the agent is what executes); only editing the opencode source (harness
  copies are separate files and already installed).
- Version bump: MANIFEST `version_added` stays `|-` for existing files; no new
  files are introduced (wording only, same paths), so no manifest change.

## Milestones
1. Skill wording.
2. Shared agent wording.
3. Per-harness wording (claude, cursor, kiro md+json) + commands/epic.md + README.
4. Mirror into `.awesome-agent/`, reinstall, verify installed copies.

## Risks
- Kiro md/json prompt bodies must stay in sync with each other (two formats,
  same text).
- Long YAML escaping pitfalls in the kiro md frontmatter — new wording goes in
  the prompt body (after the closing `---`), so plain text only; avoid YAML.
- Reinstall to every harness this machine has, or old wording stays active.
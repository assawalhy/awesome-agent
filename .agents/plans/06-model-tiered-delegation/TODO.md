# TODO — model-tiered delegation

- [x] M1: add `agents/awesome-worker.md` (shared/opencode base): subagent mode,
      description "Mechanical worker for long-running TODO items…", prompt =
      execute spec exactly, verify, report terse result, never re-plan;
      commented `# model:` example line for pinning a cheap model.
- [x] M1: add `harnesses/cursor/agents/awesome-worker.md` (`model: fast`) and
      `harnesses/claude/agents/awesome-worker.md` (`model: haiku`).
- [x] M1: MANIFEST.txt entry `agents/awesome-worker.md|0.6.0|-`; VERSION → 0.6.0
      (bumped past upstream 0.5.0 during rebase).
- [x] M2: SKILL.md — extend workflow steps 6/7 + Concepts: delegate long-running
      items to background sub-agents; light item → cheap worker, heavy reasoning
      → same-tier (inherit); workers report result + little reasoning;
      coordinator validates before ticking `[x]`.
- [x] M2: agent core rules — shared `agents/awesome-agent.md` and cursor/claude
      overlays: new rule "Delegate long work; tier the model".
- [x] M3: README: document awesome-worker, per-harness model knobs, how to pin a
      cheap model in the shared file; update file-map tree.
- [x] M3: test with fake HOME + temp project: install cursor/claude/opencode/
      codex — worker lands with right model line; codex/pi skip it; update prunes
      nothing; uninstall removes it.
- [x] M3: `./install.sh update` for all registered targets; verify `~/.cursor`,
      `~/.claude`, `~/.config/opencode` … contain awesome-worker.md.

## Revision — execution model (post-0.6.0)

- [x] `skills/awesome-plan/SKILL.md`: step 5 marks `[x]` on a minimal per-item check
      and defers tests/build; new step 7 "Verify at the end"; step 6 parallelizes as
      sub-agents in the same working tree (no worktrees), sharing PLAN.md/TODO.md,
      partitioned by disjoint files with the coordinator owning the ticks; Concepts
      "Delegation tiers" notes the shared tree.
- [x] Propagate: `agents/awesome-agent.md` (verified tracking + tiered delegation,
      description), `harnesses/{claude,cursor}/agents/awesome-agent.md` (rules 7-9,
      description), `harnesses/kiro/agents/awesome-agent.{md,json}` (description +
      How-you-work verify step + verified tracking).
- [x] README: replace the worktree-orchestration rationale with same-tree parallel
      sub-agents; adjust the live-TODO "verified" wording.
- [x] Refresh `.awesome-agent/` mirror for the changed skill + agent.
- [x] `./install.sh update --all`; verify installed targets carry the new wording and
      no workflow text still prescribes git worktrees (kiro's read-only `git worktree
      list` permission regex is unrelated and stays).

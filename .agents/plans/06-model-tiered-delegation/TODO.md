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

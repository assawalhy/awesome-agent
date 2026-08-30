# TODO

- [x] Record research findings (wshobson/agents, chezmoi, Kustomize/Helm) in PLAN.md Decisions
- [x] Create `harnesses/<id>/` overlay layout for divergent files:
      `harnesses/claude/agents/awesome-agent.md` (tools: frontmatter variant),
      `harnesses/cursor/agents/awesome-agent.md` (tools: frontmatter variant),
      `harnesses/codex/.skip` (agents/awesome-agent.md)
- [x] Rework install.sh: `src_for()` resolution (harness file -> shared -> skip),
      delete `agent_render` + `supported` flag, keep `harness_dirs` target-root mapping,
      keep codex prompts/ directory table
- [x] Update MANIFEST.txt: overlay comment (logical paths only — overlays are not
      installable entries), README (file layout, per-harness overlay rule, .skip
      semantics), VERSION bumped to 0.2.0
- [x] Verify registry migration: old logical-path entries still update/uninstall cleanly
- [x] Fake-HOME test matrix: install/update/uninstall per harness (opencode, claude, codex,
      kilo, kiro, kimi, deepseek, cursor, local) asserts correct files land and no render
      logic remains
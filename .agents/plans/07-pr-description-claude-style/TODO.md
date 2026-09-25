# TODO

- [x] Replace the source and tracked mirror with Claude's pr-description skill
- [x] Run the installer update for all registered targets
- [x] Verify all managed pr-description copies are byte-identical
- [x] Run tests and inspect the final diff for unrelated changes
  - Full suite: 38 passed, 1 expected failure, and 1 unrelated failure in `test_awesome_agent_mirror_is_synced`; the existing `agents/awesome-agent.md` mirror lacks the tiered-delegation rule.

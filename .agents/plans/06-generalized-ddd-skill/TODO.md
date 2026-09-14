# TODO

- [x] Back up `~/.claude/skills/taager-backend-architecture/SKILL.md` into
      `.agents/plans/06-generalized-ddd-skill/taager-skill.backup.md` (only copy, git-untracked)
- [x] Write `skills/ddd/SKILL.md`: detection-first opening (with the concrete `find`/`grep`
      commands to run, and "read several sibling modules, don't generalize from the first
      file"), invariants that hold in all four topologies, topology table (split /
      command-only / unsplit layered / flat) with selection rules, artifact map keyed by
      layer+role with a per-topology landing column, flows, order-of-operations, review
      checklist split into always / split-only, explicit pointers to both references
- [x] `skills/ddd/SKILL.md`: add the **Conform vs. improve** section — the three-bucket
      classifier (variation -> conform silently / defect -> don't propagate, name it once /
      typo -> don't copy), the "does it change what the code can do or which invariants hold"
      test, the frequency rule, the priority order (correctness > local consistency > canon),
      the never-overridable invariant list, and propose-don't-perform for refactors
- [x] Write `skills/ddd/references/cqrs.md`: full split canon — canonical tree, query side has
      no domain layer, projections, per-side ports & policies, command-never-reads rule,
      accepted naming variations
- [x] Write `skills/ddd/references/kotlin-spring.md`: contract-first OpenAPI generation,
      DBO/DAO/cascade persistence, native SQL constants, Specification scope, gateway-wraps-client,
      MockK/kotest/Testcontainers tiers, Spring profiles — de-Taagered
- [x] MANIFEST.txt: add `skills/ddd/SKILL.md`, `skills/ddd/references/cqrs.md`,
      `skills/ddd/references/kotlin-spring.md` at `0.5.0|-`
- [x] VERSION 0.4.0 -> 0.5.0
- [x] README: add `ddd` to the skills table, fix the "one skill" count in the intro (already
      wrong — two skills shipped), note the topology-agnostic scope in the file-layout section
- [x] Refresh `.awesome-agent/` local-harness mirror (add `skills/ddd/**`; also add the
      missing `skills/pr-description/`)
- [x] Land the Taager overlay: `allocation-service/.claude/skills/taager-backend-architecture/SKILL.md`
      — drift catalogue, `...ViewPolicy`/`...Authorities` auth model, sharedkernel-Feign
      centralization, blog citation; references the generic `ddd` skill rather than restating it.
      Check `allocation-service/.gitignore` for `.claude/` and report whether it would be committed
- [x] Remove `~/.claude/skills/taager-backend-architecture/` (after the backup step is verified)
- [x] Verify: fake-HOME `install` -> `update` -> `uninstall` for claude + codex + local places
      all three `skills/ddd/**` files and removes them cleanly
- [x] Verify: the review checklist has a "no unrequested refactors bundled into this change"
      item, and every accepted-variation entry in `references/cqrs.md` is reachable from the
      classifier's variation bucket
- [x] Verify: grep the new skill for `taager` / `Taager` / the blog citation — must be zero hits
- [x] README: add an "Auto mode + awesome-plan" section — the skill owns the
      plan -> approve -> execute gate, so harness-native plan modes are redundant; per-harness
      notes for Claude Code (`/awesome-plan`, auto/accept-edits mode) and the others
- [x] Add a global instruction to `~/.agents/AGENTS.md`: run in auto mode and let the
      `awesome-plan` skill own the planning->execution gate rather than harness plan modes
- [x] Add `.gitignore` for `.claude/` — the `local` target now resolves to `$PWD/.claude`
      (a `.claude/` dir appeared in the repo), so its install output would otherwise be
      committed alongside the tracked `.awesome-agent/` mirror

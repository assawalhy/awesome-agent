# Give each harness its own files (per-harness layouts)

> Status: **COMPLETE** (all milestones M1–M4 done, all TODO items `[x]`, test matrix green)

## Goal
Stop baking per-harness nuances into `install.sh` bash (agent_render, codex
prompts/ remap, supported=0 flags). Instead, each harness gets its own repo
files that cover its changes and nuances, following how popular large repos
organize per-platform content. install.sh just resolves and copies files.

## Approach (research-backed)
- Research how popular large repos do per-harness files (done, see Decisions):
  wshobson/agents (39k star multi-harness plugin marketplace: one source of
  truth + per-harness generated trees), chezmoi (per-OS file variants only
  where files genuinely differ), Kustomize/Helm (base + per-environment
  overlays), oh-my-zsh (per-plugin dirs).
- Adopt the **base + per-harness overlay** pattern (Kustomize/ArgoCD-style,
  the most common in large repos):
  - `commands/`, `agents/`, `skills/` stay as the SHARED base (canonical).
  - New `harnesses/<id>/` dirs hold ONLY the files that differ per harness,
    mirroring each harness's native target layout (e.g.
    `harnesses/claude/agents/awesome-agent.md`; codex gets `harnesses/codex/.skip`
    because its commands only differ by target dir, which stays a mapping).
  - Resolution in install.sh: per-harness file wins -> shared base -> skip.
- Delete `agent_render`; keep `harness_dirs` only for target-root + native
  subdir mapping. Codex "no agents" becomes an explicit per-harness exclusion
  file, not a bash flag.
- MANIFEST.txt tracks shared paths only (logical relpaths: commands/, agents/,
  skills/); overlay files are resolved at install time and tracked by their
  logical path; registry keeps old logical paths so existing installs still
  uninstall cleanly.
- Commit the overlay files (no generator/build step) to keep `./install.sh`
  one-command. Document the pattern in README.

## Decisions
- Base + overlays (not full per-harness trees, not a generator): full trees
  would duplicate 6 files x 9 harnesses and drift; wshobson/chezmoi both warn
  against hand-maintained duplication. A generator adds a build step for only
  2 divergent files today. Overlays keep duplication where divergence is real.
- Committed overlays, not gitignored/generated: users install from a plain
  clone with one command; wshobson's gitignored trees require `make generate`.
- MANIFEST keeps only logical shared paths (commands/, agents/, skills/).
  Overlay files are NOT added as installable entries: listing them would
  double-install for claude/cursor (shared + overlay to the same dest) and
  leak a variant into other harnesses via the shared-base fallback. Overlays
  are tracked by their logical path; a comment in MANIFEST documents this.
- Canonical agent stays opencode-native (permission-block frontmatter);
  opencode gets no overlay until it actually diverges.
- `harnesses/<id>/.skip` file lists shared relpaths NOT installed for that
  harness (codex: agents/awesome-agent.md). Nuances live in files, not bash.
- Codex commands map to `prompts/` via a small per-harness dir table retained
  in install.sh (target layout, not file content).

## Milestones
- [x] M1: layout + first overlays (claude, cursor agent variants; codex .skip)
- [x] M2: install.sh resolution rework (src_for + target_file), render logic removed
- [x] M3: MANIFEST/registry migration + README + VERSION 0.2.0
- [x] M4: fake-HOME install/update/uninstall green for every harness

## Risks
- Drift if a shared file is edited without checking harness overlays -> keep
  overlays minimal; README + a comment in shared files points at the rule.
- VERSION conflicts with active epic 01 (0.1.1 patch) -> coordinate: land this
  after 01 or accept 0.2.0 regardless.
- Old installs registered pre-epic logical paths must still update/uninstall
  -> registry `relpath_of` keeps resolving them.
- `.skip` semantics are new -> document in install.sh usage + README.
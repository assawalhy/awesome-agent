# Plan: Synchronize the PR description skill

## Goal

Replace the shared `pr-description` skill with Claude's 76-line version and synchronize it to the tracked mirror and every harness registered with `awesome-agent`.

## Approach

1. Copy the exact contents of `~/.claude/skills/pr-description/SKILL.md` into `skills/pr-description/SKILL.md` and `.awesome-agent/skills/pr-description/SKILL.md`.
2. Run `install.sh update --all` for the registered harness targets.
3. Verify the source, mirror, and installed copies are byte-identical.
4. Run the repository test suite and inspect the final diff for unrelated changes.

## Decisions

- Use Claude's text exactly; do not merge it with the older product/technical version.
- Update the plugin-managed targets listed in `registry.txt`.
- Leave `~/.agents/skills/pr-description` unchanged because it is not managed by this repository's installer.
- Do not bump the plugin version or create a commit.

## Milestones

- Source and mirror updated.
- All registered installations synchronized.
- Tests and final diff verified.

## Risks

- `install.sh update --all` re-copies every file in the manifest, so unrelated installed changes may be replaced.
- Claude's fixed four-backtick rule can fail if the generated description contains a longer inner fence.
- The copied skill requires a test section even when the change has no tests.

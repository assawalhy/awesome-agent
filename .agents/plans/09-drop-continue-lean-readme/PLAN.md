# Epic 09: drop /continue, lean README

## Goal

Remove the custom `/continue` command (opencode ships `/continue` as a builtin
alias of `/sessions`) and cut README.md to its essentials, with emojis, no
em-dashes, and a vertical loop diagram.

## Approach

Delete the command, mark it removed in MANIFEST at 0.7.0, bump VERSION, and
make auto-resume explicit in the awesome-plan skill. Rewrite README as a short
page: hook, install, a top-down mermaid loop, what you get, good to know,
license.

## Decisions

- Remove for all harnesses, not just opencode: the agent resumes from
  PLAN.md/TODO.md without a dedicated command.
  Rejected: `harnesses/opencode/.skip` (per-harness exception; the builtin
  stays shadowed until an update anyway).
- `commands/continue.md|0.1.0|0.7.0` so update/uninstall prune it from every
  installed target.
- One line in `skills/awesome-plan/SKILL.md` step 1: a message that only asks
  to continue resumes the active epic instead of creating a task.
- New test: `update` prunes a removed file in a fake `$HOME`, guarding the
  manifest mechanism for every future removal.
  Rejected: manual verification only.
- README hard cut: failure-mode table, example transcript and all `<details>`
  blocks go. Scope/flags survive via `./install.sh --help`, harness quirks via
  the plans dir and git history.
- Emojis in headings plus one warning bullet. No em/en dashes in the file.
- Loop diagram becomes `flowchart TD`.

## Milestones

- M1: command removal, manifest/version, skill line, prune test.
- M2: README rewrite.
- M3: verification, local install refresh.

## Risks

- Harnesses without a builtin `/continue` lose the trigger; mitigated by the
  explicit skill line.
- README loses detail (kilo paths, limitations); it lives in git history and
  `./install.sh --help`.

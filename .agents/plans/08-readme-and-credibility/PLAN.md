# Epic 08 — README that markets the plugin + close the credibility gaps

## Goal

Make `README.md` a page that sells the plugin in 30 seconds and reads cleanly, without
losing any of the reference detail it already carries. Add the three things that currently
stop a stranger from installing it: a license, a green test badge, and a repo that isn't
polluted by install output.

## Approach

One file, restructured. Visible top third = hook, pain, install, the loop, what's in the
box, a one-line-per-mechanism "how it works". Everything below the fold (auto-mode table,
scope rules, the 13 design sections, file layout, limitations) moves into `<details>`
blocks — nothing is deleted, only re-nested, and the duplicate `### 6` heading gets fixed.

New content: a pain table, a mermaid loop diagram, a realistic example session, and the
undocumented `--target local` target. Plus `LICENSE`, `.github/workflows/ci.yml`, and
untracking the committed `.awesome-agent/` install output.

The audience is reached through the *problem set*, not a label: forgetting which agent is
doing what, losing the thread after a break, mode-switching friction, the machine freezing
under parallel heavy runs, plans that are themselves a puzzle. Those are the words a
developer with ADHD recognizes in themselves; the word itself never appears.

## Decisions

- **One file with `<details>`, not a `docs/` split** — user choice. Keeps one canonical
  doc with no rot between files. Cost: collapsed text is invisible to search and to anyone
  who never expands it, so the visible part must carry the whole pitch on its own.
- **Frame the target audience through properties, never the word** — user choice, and a
  shift from the literal ask ("target people with ADHD"): the pain set and the properties
  do the targeting, so the README never says it. Need a `go` on this shift.
- **No fabricated proof** — no stars, no user counts, no benchmarks, no invented terminal
  output. The example session is written from `skills/awesome-plan/SKILL.md` so it shows
  behavior the plugin actually has.
- **Keep the per-harness run-mode table visible** — hiding it invites people to use a
  harness plan mode, which is the exact mistake the plugin exists to fix. Collapsed detail
  is fine; an instruction that breaks the workflow is not.
- **`MIT` + holder `Muhammad Assawalhy`, year 2026** — from `git config`. Easy to change.
- **CI = python tests + `bash -n install.sh` only** — shellcheck isn't installed locally, so
  adding a lint job risks a red badge on first push. `bash -n` is honest and green.
- **Do not commit, do not rewrite history** — I stage the index change for untracking and
  leave the commit to you.
- **Fix the typos in the pain list** (`frozes`, `ot`, `dicision`, `opnion`, `tradoffs`) —
  that section is the hook; it has to read clean.
- **Leave the repo's own `.agents/plans/` epics untouched** — they're the plugin dogfooding
  itself; only 08 is new.

## Milestones

- M1 — repo hygiene + trust signals: untrack install output, LICENSE, CI, badge.
- M2 — README visible half rewritten (hook → pain table → install → loop → box → how it works).
- M3 — deep sections nested under `<details>`, numbering fixed, nothing lost.

## Risks

- **Collapsed content is invisible** → the visible "how it works" list has to be a complete
  pitch on its own, and every `<summary>` must state the value, not the topic
  ("Why one gate beats a plan mode", not "Gate").
- **`<details>` markdown silently stops rendering** without a blank line after `<summary>`
  → every block gets checked; that's an explicit TODO.
- **A marketing rewrite can drift into claims the code doesn't support** → the example
  session is derived from the skill file, and TODO 8 sweeps for unverified claims.
- **Untracking `.awesome-agent/` changes the index** → done as `git rm --cached` only, no
  history rewrite, reported clearly.
- **GitHub renders `<details>` but not all viewers do** (raw markdown, some editors) → the
  deep sections are still present as plain text, so nothing is lost in the worst case.

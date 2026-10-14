# Epic 10: README shows the pain points again

## Goal

Put the pain points and how awesome-agent answers them back into README.md,
without undoing epic 09's lean structure. The 82-line page tells what the tool
does but not what breaks without it.

## Context

- Epic 09 hard-cut the failure-mode table and the example session. Its own risk
  note says the loss is accepted because git history keeps it.
- The pre-09 README (git show 2f2976f~1:README.md, 428 lines) had: a 9-row
  failure-mode table, a 7-bullet how-it-works list, and a `/epic` session mock.
- Of those, only the pain table and the session mock actually sell the tool.
  The deep `<details>` reference sections stay cut.
- README.md is not installed and not in MANIFEST.txt, so no installer or
  version mechanics are involved.

## Approach

Edit README.md in place at three insertion points.
Everything epic 09 kept (hook, install, ajq tip, mermaid loop, what you get,
good to know, license) stays as is.

1. After the hook paragraph: "What goes wrong" table, 9 rows updated for the
   current feature set. The `/continue` row becomes the resume row using the
   current mechanism: tell the agent to continue, it reads the active plan
   and `TODO.md`.
2. Under the table: "What it comes down to", 4 bold-lead bullets condensed from
   the old how-it-works section.
3. Under The loop: the condensed `/epic` session mock (plan review, `go`,
   checklist ticking), verbatim from the pre-09 README except the parts that
   referenced removed behavior.

Target length ~135 lines, up from 82, still far under the old 428.

## Decisions

- Restore pain content into README.md itself, not a linked page: the README is
  the one page a visitor reads; a second file splits the pitch.
  Rejected: separate docs/PAIN-POINTS.md (pitch hides behind a link).
- Table + bullets + session mock, not the full pre-09 restore: epic 09 cut the
  reference detail for a reason and this ask does not reopen it.
  Rejected: restore 428-line README (reintroduces the wall epic 09 removed).
- Session mock returns because it shows the gate and the live checklist, which
  is the behavior nothing else on the page demonstrates.
- Keep epic 09's style: emojis in headings, flowchart TD loop, no em or en
  dashes anywhere in the file.
- No VERSION bump: docs-only change, MANIFEST and installer untouched.

## Milestones

- M1: README rewrite in place (table, bullets, session mock).
- M2: verify style and content checks.

## Risks

- Table rows that run long read as prose and lose skimmability: keep one line
  per row, name the concrete artifact in the fix column.
- Session mock drifts from what the agent actually does: copy it from the
  pre-09 file, which epic 08 vetted against the skill, and drop only the
  `/continue`-era bits (the mock has none).
- This revises an epic 09 decision; the old text stays in git history, so the
  shift is one revert away if you change your mind.

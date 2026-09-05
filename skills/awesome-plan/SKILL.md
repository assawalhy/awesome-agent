---
name: awesome-plan
description: Plan-first workflow for awesome-agent — draft a readable plan, request approval, execute, and orchestrate parallel worktree agents.
---

# awesome-plan

Use this skill at the start of every awesome-agent task.

## 0. Balance: fast path first

Skip the plan + approval steps and go straight to execution when:
- the change is very small (a one-line fix or a single-file tweak), or
- the user's message already contains the plan/instructions to follow.

Everything else proceeds through steps 1–4. When unsure, default to planning.

## 1. Place or create the epic

- List ACTIVE epics: any `.agents/plans/<NN>-<slug>/` whose `TODO.md` still has open
  `- [ ]` items. Add the task to the epic it clearly belongs to (match its PLAN.md goal).
- If several match, ask the user which epic this belongs to.
- If no active epic fits the task, ASK the user whether to create a new epic — do not
  invent one silently.
- To start a NEW epic: create `.agents/plans/<NN+1>-<slug>/` (slug = 2-4 lowercase words).

## 1.5 Research before Decisions (mandatory for non-trivial work)

Before writing PLAN.md, resolve every non-obvious question yourself — do not defer
decisions to execution:

- Research the repo (code, data, prior epics), official docs, and the web for existing
  solutions and best practices; compare real options with sources.
- Every Approach/Decisions entry in PLAN.md must carry a one-line rationale (and a source
  where one exists). Rejected alternatives are named with why they lost.
- "Spike", "pick the winner later", "decide during execution" phrasing is FORBIDDEN for
  anything the user is being asked to approve. If something genuinely cannot be decided
  before approval, put an explicit research TODO at the TOP of TODO.md and say so in the
  approval ask — never hide an open decision inside implementation work.
- Trivial tasks (step 0 fast path) skip this step entirely.

## 2. Write PLAN.md

Keep it short and human-readable:

```
# <Epic title>

## Goal
One or two sentences a human can scan.

## Approach
- Step one
- Step two

## Decisions
- Choice X because <one line>

## Milestones
- M1: ...
- M2: ...

## Risks
- <anything that could go wrong>
```

## 3. Write TODO.md

A checklist of small, verifiable items, in execution order:

```
# TODO

- [ ] <first actionable item>
- [ ] <next item>
```

Each item must be independently checkable.

## 4. Ask for approval

Print a 5-line summary (goal + first 3 TODO items) and end your turn with:

> Reply `go` to execute this plan, or type feedback to refine it.

Do not proceed past this point without an explicit `go`.

## 5. On `go` — execute

- Work items top to bottom.
- After each, run the checks the task needs (syntax gate, tests/e2e).
- Mark `- [x]` only when verified. Update TODO.md as new tasks appear.

## 6. On feedback — refine

- Fold the user's feedback into PLAN.md and TODO.md.
- Return to step 4 and ask for `go` again.

## 7. Orchestrate parallel work

When several TODO items are independent:

- `git worktree add .worktrees/<name> -b <branch>`
- Launch one sub-agent (Task tool) per worktree, scoped to that directory.
- When all sub-agents finish, merge the branches and remove the worktrees.

## 8. Start a new session

To begin a different effort, create the next plan dir and delegate execution to a fresh
sub-agent so the supervising session stays available for review.

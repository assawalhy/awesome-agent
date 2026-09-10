---
name: awesome-plan
description: Plan-first workflow — research, draft a readable plan, get approval, execute, track in TODO.md.
---

# awesome-plan

Core loop: **research → plan → approve → execute → track**.

## Concepts

- **Epic**: a `.agents/plans/<NN>-<slug>/` dir holding `PLAN.md` (what/why) and
  `TODO.md` (checklist). An epic is *active* while its TODO.md has open `- [ ]` items.
- **Fast path**: skip plan+approval when the change is trivial (one-liner,
  single-file tweak) or the user's message already is the plan. When unsure, plan.
- **Approval gate**: never execute a non-trivial plan before the user replies `go`.
  Feedback → refine the plan → ask again.
- **Decided plans**: a plan shown for approval contains decisions, not open questions.
- **Visual-first review**: approval summaries use show-me style visuals (trees,
  flows, diffs) over prose — the user should grasp the plan at a glance.

## Workflow

1. **Place the task.** Add it to the active epic whose goal it matches. Several
   match → ask which. None fits → ask before creating a new epic. Never invent
   one silently.
2. **Research before deciding.** Resolve non-obvious questions from code, docs,
   web, and prior epics *before* writing the plan. Compare real options; name
   rejected alternatives and why they lost. Surface trade-offs, limitations, and
   contradictions to the user rather than picking silently. If something is truly
   undecidable, make it the first TODO item and flag it in the approval ask —
   never hide an open decision inside implementation work.
3. **Draft the plan.** PLAN.md sections: Goal, Approach, Decisions (one-line
   rationale each), Milestones, Risks — short, one idea per line. TODO.md: small,
   independently verifiable items in execution order.
4. **Ask approval — visual-first, like the show-me skill.** Brief prose,
   then the smallest visuals that make the plan reviewable: a file tree for
   scope, a mermaid or flow sketch for the approach, a diff-shaped sketch when
   changing existing structures, one line per decision with its rationale. End
   with: "Reply `go` to execute, or give feedback to refine." Then stop.
5. **Execute on `go`.** Work top to bottom. Mark `[x]` only when verified
   (syntax + tests as applicable). Keep TODO.md current as scope evolves.
6. **Parallelize independent items.** One git worktree + one scoped sub-agent
   each; merge and clean up when done — only worktrees you created.
7. **New effort → new session.** Create the next epic dir and delegate execution
   to a fresh sub-agent; this session supervises and validates.

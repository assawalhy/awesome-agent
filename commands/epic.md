---
description: Plan a big feature/epic with awesome-plan, then start building it
---

# /epic

Create a new epic for a substantial feature or goal, plan it, then build.

1. ALWAYS plan first. Run the **awesome-plan** skill: it runs the grill-me style interview
   (relentless clarifying questions about goal, approach, risks, edge cases, and what "done"
   means), then drafts `PLAN.md` and `TODO.md`. Do not write any implementation code until
   the plan is settled and the user has decided (they reply `go`, or give feedback to refine).
2. The skill places the epic at `.agents/plans/<NN+1>-<slug>/` (next free number).
3. Review existing work in the repo for relevant context and conflicts before building.
4. Start executing the first TODO items. Keep `TODO.md` accurate as new tasks appear.
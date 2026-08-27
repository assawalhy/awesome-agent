---
description: Start executing the current plan autonomously; fall back to manual if no plan exists
---

# /go

Execute the active plan automatically.

1. Find the active epic: the highest-numbered `.agents/plans/<num>-<epic>/` that has a
   `PLAN.md` and/or `TODO.md`.
2. If a plan exists: read `TODO.md` and start completing tasks automatically, one by one,
   marking `- [x]` when verified. Treat the plan's open questions as already answered —
   proceed without re-asking.
3. If the plan (or its question context) is missing or lost: fall back to MANUAL mode.
   Tell the user no plan was found and ask them to create one with `/epic` (or `/todo`),
   then wait for their input before doing anything.
4. Keep working through the epic until every item is done or you hit a blocker that truly
   needs the user.

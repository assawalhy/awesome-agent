---
description: Start executing the current plan autonomously; fall back to manual if no plan exists
---

# /go

Execute the active epic's TODO.md top to bottom, autonomously — per the
**awesome-plan** skill.

- Treat the plan's questions as already answered; proceed without re-asking.
- If no plan exists, say so and ask the user to create one with `/epic` or
  `/todo`; wait for input.
- Stop only when everything is done or you hit a blocker that truly needs the
  user.

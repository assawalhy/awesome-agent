---
description: Add a new task to the current epic's TODO and start working after current WIP is done
---

# /todo

Add a new task and then execute it, respecting in-progress work.

1. Find the active epic: look in `.agents/plans/` for the highest-numbered `<num>-<epic>/`
   directory. If several exist, ask the user which epic this task belongs to if you can certainly pick one.
2. If no epic exists yet, create one: `mkdir -p .agents/plans/NN-<slug>` and seed a
   `PLAN.md` (for a big feature, use `/epic` instead).
3. Open that epic's `TODO.md` (create it with a `# TODO` header if missing).
4. Finish whatever you are currently doing (your in-progress WIP task) before starting
   the new one — never leave half-done work behind.
5. Append the new task from `$ARGUMENTS` as a `- [ ] <task>` line.
6. Once the current WIP is wrapped up, start the new task. Mark `- [x]` only when it is
   actually finished and verified.

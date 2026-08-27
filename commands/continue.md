---
description: Continue unfinished work, review TODO.md, and check sub-agents and background jobs
---

# /continue

Pick up where the work left off and drive unfinished tasks to completion.

1. Read the active epic's `TODO.md` (in `.agents/plans/<num>-<epic>/`). List every
   unfinished `- [ ]` item.
2. Check for running sub-agents and background jobs (e.g. task-tool runs, background
   processes, queued agents) and report their status before kicking off new work. Wait
   for or reconcile any in-flight jobs.
3. Work through the unfinished TODO items in order. Stay focused: finish before starting
   unrelated tasks.
4. Verify each task (syntax gate + tests/e2e where applicable) and mark `- [x]` only when
   truly done.
5. If `TODO.md` is empty or missing, tell the user there is nothing queued and offer to
   create one with `/todo` or `/epic`.

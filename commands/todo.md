---
description: Add a task to the active epic it belongs to, then start it after current WIP
---

# /todo

Add a task to the epic it belongs to, then execute it.

1. List active epics: in `.agents/plans/`, any `<NN>-<slug>` whose `TODO.md` still has
   unfinished `- [ ]` items.
2. Pick the epic the task most clearly belongs to, judging from its `PLAN.md` goal/title.
   - If exactly one active epic matches, use it.
   - If several match, ask the user which epic this task belongs to.
3. If the task does NOT fit any active epic, stop and ASK the user whether to create a new
   epic for it (or leave it untracked). Never silently invent a new epic without asking.
4. Append `- [ ] <task>` from `$ARGUMENTS` to that epic's `TODO.md` (create the file with a
   `# TODO` header if missing).
5. Finish whatever you are currently doing (your in-progress WIP task) before starting the
   new one — never leave half-done work behind.
6. Start the task. Mark `- [x]` only when it is actually finished and verified.
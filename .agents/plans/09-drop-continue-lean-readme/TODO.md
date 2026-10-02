# TODO: Epic 09

- [x] 1. Delete `commands/continue.md`; MANIFEST -> `commands/continue.md|0.1.0|0.7.0`;
      VERSION -> 0.7.0; install.sh header comment 4 commands -> 3.
      Check: `grep -rn 'commands/continue' --exclude-dir=.git .` only hits MANIFEST.
- [x] 2. `skills/awesome-plan/SKILL.md` step 1: a message that only asks to
      continue resumes the active epic.
- [x] 3. Test: `install.sh update` prunes a removed file in a fake HOME.
- [x] 4. Rewrite README.md short (emojis, no em/en dashes, `flowchart TD`).
- [x] 5. Verify: `bash -n install.sh`, full suite, prune sim, fresh-clone CI sim,
      dash grep, line count, mermaid render.
- [x] 6. Refresh local installs: `--target local` prune, then `update` on the
      real opencode install so the builtin `/continue` is unshadowed.

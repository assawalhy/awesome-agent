# TODO — Epic 08

## Parallel-safe split: [1,2,3] worker (mechanical) · [4,5,6,7,8] coordinator (README)

- [x] 1. Untrack the committed install output: `git rm -r --cached .awesome-agent`, add
      `.awesome-agent/` to `.gitignore` next to the existing `.claude/` + `.cursor/` lines.
      Verify: `git status` no longer lists it, `git check-ignore -v .awesome-agent` matches.

- [x] 2. Add MIT `LICENSE` (holder `Muhammad Assawalhy`, 2026, from `git config`) and a
      License line in the README pointing at it. Verify: `git ls-files LICENSE` resolves,
      README link path is correct.

- [x] 3. Add `.github/workflows/ci.yml`: on push/PR to main, run
      `python3 tests/test_awesome_agent.py` and `bash -n install.sh`. Add the resulting
      badge as the first line of the README.
      Verify: workflow YAML parses, `python3 tests/test_awesome_agent.py` is green
      (expect 40 tests, 1 skip, 1 expected failure), `bash -n install.sh` exits 0.

- [x] 4. Rewrite the visible head of `README.md`: hook line, pain→fix table (typos fixed,
      "I faced some issues" voice dropped), 60-second install including the undocumented
      `--target local` target, the "what you get" table kept and tightened.
      Verify: reads top-down in 30 seconds, every install command is copy-pasteable and
      actually appears in `./install.sh --help` or the script.

- [x] 5. Add the loop: a mermaid diagram of research → plan → `go` → execute → verify, and a
      realistic example session written from `skills/awesome-plan/SKILL.md` (no invented
      output). Verify: mermaid syntax valid, every claim in the session traceable to the
      skill file or a command file.

- [x] 6. Add a visible "how it works" list — one line per mechanism, phrased as the property
      it buys (never lose the thread, one gate instead of mode switching, live checkmarks,
      resume in one word, one heavy queue, nothing to remember between sessions).
      Verify: `grep -inE 'adhd|attention.?deficit|hyperfocus' README.md` returns nothing;
      every bullet maps to a real mechanism in `commands/`, `agents/` or `skills/`.

- [x] 7. Nest the deep sections under `<details>`: auto-mode per-harness table, scope rules,
      design rationale (fix the duplicate `### 6`), file layout, limitations. Every
      `<summary>` states the value, every block has a blank line after `<summary>`.
      Verify: no duplicate heading numbers, and a section-by-section diff against the
      pre-change README shows nothing dropped.

- [x] 8. Final verification: render the markdown, check every internal link and anchor,
      sweep for typos and for claims the code doesn't support, confirm the documented
      flags still match `./install.sh --help`.
      Verify: clean read-through top to bottom, no dead links, `--help` output matches.

## Fact-check pass (added after the rewrite, per review)

Every claim in the limitations and auto-mode sections checked against `install.sh` and the
harness overlays. Six defects found and fixed:

- [x] 9. Removed the `grill-me` limitation: `grep -rn grill` has zero hits in the repo — it
      described the author's personal global skill, not anything a reader of this plugin has.
- [x] 10. Removed the unverifiable "pi v0.84.x" version claim (no source in the repo, rots
      on the next pi release) and replaced it with a rot-proof "re-check after a pi update".
- [x] 11. Corrected the codex/pi bullets: both `.skip` files list *two* agent files
      (`awesome-agent.md` **and** `awesome-worker.md`), not "the agent file".
- [x] 12. Dropped kilo from the "verified mappings" list and documented the real split:
      global → `~/.config/kilo` for commands/agents but `~/.kilocode/skills`;
      `kilo:local` → `.kilo/`; `--target local` → `.kilocode/`.
- [x] 13. Documented that `--target local` will still write into `.codex/`, `.kimi-code/` or
      `.deepseek/` when such a folder exists, even though those harnesses are global-only for
      the *scope* choice — the old wording implied they can never be installed locally.
- [x] 14. Replaced the invented "items needing the same file run in sequence" guarantee with
      what the skill actually says: the coordinator must partition by disjoint files, and the
      skill requires that but does not enforce it.
- [x] 15. Rewrote the Kiro row of the auto-mode table: the install ships deny-by-default
      shell rules (~265 allow patterns, `ask` on secrets/deploy dirs/metacharacters), not a
      mode toggle — verified from `harnesses/kiro/agents/awesome-agent.json`.

# Make awesome-agent opencode's default agent via installer

## Goal
When `install.sh` installs into the `opencode` harness, also set
`"default_agent": "awesome-agent"` in `~/.config/opencode/opencode.json(.c)`
so awesome-agent becomes the default agent. Uninstall reverts it.

## Approach
- Add pure-bash helpers to install.sh:
  - `opencode_config_file()` — locate `~/.config/opencode/opencode.json` or `.jsonc`
  - `opencode_set_default()` — idempotently set `default_agent` to `awesome-agent`
    (replace existing value, else insert after `$schema`/first `{`); record the
    previous value in a state file so uninstall can restore it
  - `opencode_unset_default()` — restore the recorded previous value, else remove
    the `default_agent` key (opencode then falls back to `build`)
- All edits atomic via tmp file + mv.
- Wire `opencode_set_default` into `do_install` (install + update modes) and
  `opencode_unset_default` into `do_uninstall`, for the `opencode` target only.
- Best-effort validation: if `python3` exists, validate with `python3 -m json.tool`;
  otherwise skip silently.
- Document in README; bump VERSION with a **patch** version increase
  (0.1.0 -> 0.1.1, not a minor bump).

## Decisions
- Only the `opencode` harness is touched. Other harnesses have different config
  mechanisms; `local` is excluded because it is project-scoped.
- Revert-on-uninstall restores the user's previous value (state file) instead of
  dropping the key outright, to avoid clobbering an existing `default_agent: plan`.
- Pure bash (no new dependencies), matching the installer's no-deps design.

## Milestones
- M1: helpers + wiring in install.sh
- M2: README + VERSION patch bump (0.1.0 -> 0.1.1)
- M3: simulated install / update / uninstall test with a fake HOME passes

## Risks
- Malformed JSON if the user's config has comments/odd formatting. Mitigated by
  atomic tmp+mv and optional python3 validation; opencode hard-fails on bad config
  so this is checked before restart.
- `update` overwrites a manually-changed `default_agent` — acceptable, that is the
  "awesome-agent is the default" contract.
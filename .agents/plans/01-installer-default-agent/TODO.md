# TODO

- [x] Add pure-bash helpers `opencode_config_file`, `opencode_set_default`, `opencode_unset_default` (atomic tmp+mv, handles .json/.jsonc, records previous value in state file)
- [x] Call `opencode_set_default` from `do_install` for target `opencode` (install + update modes)
- [x] Call `opencode_unset_default` from `do_uninstall` for target `opencode`
- [x] Best-effort JSON validation after edit (python3 -m json.tool when available, else skip)
- [x] Update README (What you get + install/update/uninstall notes)
- [x] Bump VERSION to 0.1.1 (patch version increase, not minor)
- [x] Test with fake HOME: install sets default_agent, update is idempotent, uninstall restores previous value / removes key
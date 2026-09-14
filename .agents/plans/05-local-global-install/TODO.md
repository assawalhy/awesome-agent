# TODO

- [x] M1: split `harness_dirs` into global/local tables (`harness_dirs_global`,
      `harness_dirs_local`), add `harness_scopes`/`scope_supported`/`harness_localdir`,
      cursor global = `$HOME/.cursor`
- [x] M1: `target_file` takes scope; registry keyed `id:scope` (add/get/remove) +
      one-time `migrate_registry` (bare `cursor`/`local` -> `:local`, else `:global`)
- [x] M1: `do_install`/`do_uninstall` take `id scope`; opencode `default_agent` only for
      `opencode:global`
- [x] M2: interactive second multi-select for scope (globals pre-selected, `both` =
      select both); `multiselect` supports `MS_TITLE`/`MS_PRESELECT`
- [x] M2: CLI `--scope global|local|both` + `id:scope` in `--target`; expand/dedupe pairs;
      `--all` = global, `--all --scope both` = both
- [x] M3: README (scope docs + rationale + limitations), `usage()`, VERSION 0.4.0
- [x] M4: fake-HOME/temp-project tests: global+local install, `--scope both`, global-only
      fallback, explicit unsupported rejection, update/uninstall per scope, registry
      migration from a legacy file, interactive target+scope TUI and TUI uninstall

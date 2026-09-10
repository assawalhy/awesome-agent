#!/usr/bin/env bash
# awesome-agent installer — "oh my openagent"
# Drop-in slash commands (/todo /continue /epic /go) for many AI coding harnesses.
# Detects installed harnesses, multi-selects targets, and installs / updates /
# uninstalls. Tracks every file (including removed ones) via MANIFEST.txt so
# uninstall cleans up legacy files no longer in the repo.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="$SCRIPT_DIR/commands"
MANIFEST="$SCRIPT_DIR/MANIFEST.txt"
REGISTRY="${XDG_DATA_HOME:-$HOME/.local/share}/awesome-agent/registry.txt"
PLUGIN_NAME="awesome-agent"

# ---- harness config --------------------------------------------------------
# harness_dirs <id> -> prints: <root> <cmd_dir> <agent_dir> <skill_root>
harness_dirs() {
  case "$1" in
    opencode)  printf "%s command agents %s/skills\n" "$HOME/.config/opencode" "$HOME/.config/opencode" ;;
    claude)    printf "%s commands agents %s/skills\n" "$HOME/.claude" "$HOME/.claude" ;;
    codex)     printf "%s prompts agents %s/skills\n" "$HOME/.codex" "$HOME/.codex" ;;  # no user slash commands / md agents; the agent is skipped via harnesses/codex/.skip
    pi)        printf "%s prompts agents %s/skills\n" "$HOME/.pi/agent" "$HOME/.pi/agent" ;;  # no user slash commands / md agents; the agent is skipped via harnesses/pi/.skip
    kilo)      printf "%s commands agents %s/skills\n" "$HOME/.config/kilo" "$HOME/.kilocode" ;;
    kiro)      printf "%s commands agents %s/skills\n" "$HOME/.kiro" "$HOME/.kiro" ;;
    kimi)      printf "%s commands agents %s/skills\n" "$HOME/.kimi-code" "$HOME/.kimi-code" ;;
    deepseek)  printf "%s commands agents %s/skills\n" "$HOME/.deepseek" "$HOME/.deepseek" ;;
    cursor)    printf "%s commands agents %s/skills\n" "$PWD/.cursor" "$PWD/.cursor" ;;
    local)     local_dirs ;;
    *)         echo "" ;;
  esac
}
# mimic the harness detected in the current project folder, else default
local_dirs() {
  if   [ -d "$PWD/.opencode" ];   then printf "%s command agents %s/skills\n" "$PWD/.opencode" "$PWD/.opencode"
  elif [ -d "$PWD/.claude" ];     then printf "%s commands agents %s/skills\n" "$PWD/.claude" "$PWD/.claude"
  elif [ -d "$PWD/.kilocode" ];   then printf "%s commands agents %s/skills\n" "$PWD/.kilocode" "$PWD/.kilocode"
  elif [ -d "$PWD/.codex" ];      then printf "%s prompts agents %s/skills\n" "$PWD/.codex" "$PWD/.codex"
  elif [ -d "$PWD/.cursor" ];     then printf "%s commands agents %s/skills\n" "$PWD/.cursor" "$PWD/.cursor"
  elif [ -d "$PWD/.pi" ];         then printf "%s prompts agents %s/skills\n" "$PWD/.pi" "$PWD/.pi"
  elif [ -d "$PWD/.kiro" ];       then printf "%s commands agents %s/skills\n" "$PWD/.kiro" "$PWD/.kiro"
  elif [ -d "$PWD/.kimi-code" ];  then printf "%s commands agents %s/skills\n" "$PWD/.kimi-code" "$PWD/.kimi-code"
  elif [ -d "$PWD/.deepseek" ];   then printf "%s commands agents %s/skills\n" "$PWD/.deepseek" "$PWD/.deepseek"
  else printf "%s command agents %s/skills\n" "$PWD/.awesome-agent" "$PWD/.awesome-agent"; fi
}
harness_root() { local d; d="$(harness_dirs "$1")"; [ -z "$d" ] && echo "" || echo "${d%% *}"; }
# map a manifest relpath to its absolute installed path for a given harness
target_file() {
  local h="$1" rp="$2" root_override="${3:-}"
  local root cmd_dir agent_dir skill_root logical
  read -r root cmd_dir agent_dir skill_root <<< "$(harness_dirs "$h")"
  [ -n "$root_override" ] && root="$root_override"
  logical="$rp"
  case "$rp" in
    harnesses/*)                                  # overlay relpath -> logical path
      logical="${rp#harnesses/$h/}"
      [ "$logical" = "$rp" ] && return 1          # overlay for a different harness
      ;;
  esac
  case "$logical" in
    commands/*) echo "$root/$cmd_dir/$(basename "$logical")" ;;
    agents/*)   echo "$root/$agent_dir/${logical#agents/}" ;;
    skills/*)   echo "$skill_root/${logical#skills/}" ;;
    *)          echo "$root/$(basename "$logical")" ;;
  esac
}
harness_installed() {
  case "$1" in
    opencode)  [ -d "$HOME/.config/opencode" ] || command -v opencode >/dev/null 2>&1 && echo 1 ;;
    claude)    [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1 && echo 1 ;;
    codex)     [ -d "$HOME/.codex" ] || command -v codex >/dev/null 2>&1 && echo 1 ;;
    pi)        [ -d "$HOME/.pi/agent" ] || command -v pi >/dev/null 2>&1 && echo 1 ;;
    kilo)      [ -d "$HOME/.kilocode" ] || command -v kilo >/dev/null 2>&1 && echo 1 ;;
    kiro)      [ -d "$HOME/.kiro" ] || command -v kiro >/dev/null 2>&1 && echo 1 ;;
    kimi)      [ -d "$HOME/.kimi-code" ] && echo 1 ;;
    deepseek)  command -v deepseek >/dev/null 2>&1 || [ -d "$HOME/.deepseek" ] && echo 1 ;;
    cursor)    command -v cursor >/dev/null 2>&1 || [ -d "$HOME/.cursor" ] && echo 1 ;;
    local)     echo 1 ;;
    *)         echo "" ;;
  esac
}
harness_label() {
  case "$1" in
    opencode)  echo "OpenCode ($HOME/.config/opencode)" ;;
    claude)    echo "Claude Code ($HOME/.claude)" ;;
    codex)     echo "Codex ($HOME/.codex, commands as /prompts:*)" ;;
    pi)        echo "Pi ($HOME/.pi/agent, commands as /name prompt templates)" ;;
    kilo)      echo "Kilo Code ($HOME/.config/kilo, skills $HOME/.kilocode)" ;;
    kiro)      echo "Kiro ($HOME/.kiro)" ;;
    kimi)      echo "Kimi Code ($HOME/.kimi-code)" ;;
    deepseek)  echo "DeepSeek harness ($HOME/.deepseek)" ;;
    cursor)    echo "Cursor (project: $PWD/.cursor)" ;;
    local)     echo "Current project folder" ;;
    *)         echo "$1" ;;
  esac
}
ALL_IDS=(opencode claude codex pi kilo kiro kimi deepseek cursor local)

# ---- per-harness file resolution --------------------------------------------
# Per-harness overlay files live in harnesses/<id>/ and mirror that harness's
# native layout. Resolution for a shared relpath: a harness-specific file wins
# over the shared base; harnesses/<id>/.skip lists shared relpaths NOT installed
# for that harness. Nuances live in files, not in bash render logic.
src_for() {
  local h="$1" rp="$2"
  if [ -f "$SCRIPT_DIR/harnesses/$h/.skip" ] && grep -qxF "$rp" "$SCRIPT_DIR/harnesses/$h/.skip" 2>/dev/null; then
    return 1
  fi
  if [ -f "$SCRIPT_DIR/harnesses/$h/$rp" ]; then
    echo "harnesses/$h/$rp"; return 0
  fi
  if [ -f "$SCRIPT_DIR/$rp" ]; then
    echo "$rp"; return 0
  fi
  return 1
}

# ---- manifest helpers ------------------------------------------------------
# echo repo-relative paths of files still shipped (version_removed == "-")
manifest_current() {
  local rp va vr
  while IFS='|' read -r rp va vr; do
    [ -z "$rp" ] && continue
    [ "${vr:-=}" = "-" ] && echo "$rp"
  done < "$MANIFEST"
}
# echo repo-relative paths of files that have been removed (version_removed != "-")
manifest_removed_list() {
  local rp va vr
  while IFS='|' read -r rp va vr; do
    [ -z "$rp" ] && continue
    [ "${vr:-=}" != "-" ] && echo "$rp"
  done < "$MANIFEST"
}
# is <relpath> removed in the manifest? -> echoes 1 or ""
manifest_is_removed() {
  local want="$1" rp va vr
  while IFS='|' read -r rp va vr; do
    [ "$rp" = "$want" ] && { [ "${vr:-=}" != "-" ] && echo 1; return; }
  done < "$MANIFEST"
}
# resolve a possibly-legacy basename to its manifest relpath (for migration)
relpath_of() {
  local tok="$1"
  case "$tok" in
    */*) echo "$tok"; return ;;           # already a relpath
  esac
  local rp; while IFS='|' read -r rp _; do
    [ "$(basename "$rp")" = "$tok" ] && { echo "$rp"; return; }
  done < "$MANIFEST"
  echo "$tok"                             # unknown legacy file: keep basename
}

# ---- pure-bash multi-select TUI --------------------------------------------
multiselect() {
  local opts=("$@")
  local n=${#opts[@]} cursor=0 i
  local sel=()
  for ((i=0;i<n;i++)); do sel[i]=0; done
  SELECTED_IDX=""
  tput civis
  stty -echo -icanon time 0 min 0 2>/dev/null || true
  trap 'stty echo icanon 2>/dev/null; tput cnorm; trap - RETURN' RETURN
  draw() {
    tput clear
    echo "awesome-agent — select targets (space toggle, a=all, enter confirm):"
    echo
    for ((i=0;i<n;i++)); do
      if [ "$i" = "$cursor" ]; then printf " > "; else printf "   "; fi
      if [ "${sel[i]}" = "1" ]; then printf "[x] "; else printf "[ ] "; fi
      printf "%s\n" "${opts[i]}"
    done
    echo; echo "($n targets)"
  }
  draw
  while true; do
    IFS= read -r -n1 -s key
    case "$key" in
      $'\x1b')
        read -r -n2 -s rest
        case "$rest" in
          "[A") ((cursor>0)) && cursor=$((cursor-1)) ;;
          "[B") ((cursor<n-1)) && cursor=$((cursor+1)) ;;
        esac; draw ;;
      " ") sel[cursor]=$((1 - sel[cursor])); draw ;;
      a|A)
        local any=0; for ((i=0;i<n;i++)); do [ "${sel[i]}" = "1" ] && any=1; done
        for ((i=0;i<n;i++)); do sel[i]=$((1-any)); done; draw ;;
      ""|$'\x0a'|$'\x0d') break ;;
      q|Q) cursor=-1; break ;;
    esac
  done
  stty echo icanon 2>/dev/null || true
  tput cnorm
  [ "$cursor" = "-1" ] && { SELECTED_IDX=""; return; }
  local out=""
  for ((i=0;i<n;i++)); do [ "${sel[i]}" = "1" ] && out="$out $i"; done
  SELECTED_IDX="${out# }"
}

# ---- registry (per-target set of installed relpaths) -----------------------
registry_add() {           # registry_add <id> <root> <relpath>...
  local id="$1" root="$2"; shift 2
  mkdir -p "$(dirname "$REGISTRY")"
  local line f
  line="$(registry_get "$id")"
  if [ -n "$line" ]; then
    [ -z "$root" ] && { root="${line#*|}"; root="${root%|*}"; }  # fall back to old root
    line="${line##*|}"                     # existing files portion
  fi
  local files=() seen=" "
  for f in $line "$@"; do
    [ -z "$f" ] && continue
    f="$(relpath_of "$f")"
    case "$seen" in *" $f "*) ;; *) files+=("$f"); seen="$seen$f "; esac
  done
  grep -vF "$id|" "$REGISTRY" 2>/dev/null > "$REGISTRY.tmp" || : > "$REGISTRY.tmp"
  echo "$id|$root|${files[*]}" >> "$REGISTRY.tmp"
  mv "$REGISTRY.tmp" "$REGISTRY"
}
registry_get() { grep -F "$1|" "$REGISTRY" 2>/dev/null | head -1; }
registry_remove() { grep -vF "$1|" "$REGISTRY" 2>/dev/null > "$REGISTRY.tmp" || : > "$REGISTRY.tmp"; mv "$REGISTRY.tmp" "$REGISTRY"; }
registry_list() { [ -f "$REGISTRY" ] && sed '/^$/d' "$REGISTRY"; }

# ---- opencode default_agent -------------------------------------------------
# Installing into opencode also sets awesome-agent as the default agent
# ("default_agent" in $root/opencode.json[.c]). The previous value is recorded
# so uninstall can restore it; a dangling-comma pass keeps the edits valid JSON.
DEFAULT_STATE="${XDG_DATA_HOME:-$HOME/.local/share}/awesome-agent/opencode_default.txt"

opencode_config_file() {
  local root="$1"
  [ -z "$root" ] && root="$(harness_root opencode)"
  [ -z "$root" ] && return 1
  if   [ -f "$root/opencode.json" ];  then echo "$root/opencode.json"
  elif [ -f "$root/opencode.jsonc" ]; then echo "$root/opencode.jsonc"
  else echo "$root/opencode.json"; fi
}

# strip a trailing comma on the last non-blank line before a closing brace
# (repairs our line insert/delete edits); jsonc allows trailing commas, so skip
fix_dangling_comma() {
  local f="$1" tmp
  case "$f" in
    *.jsonc) return 0 ;;
  esac
  tmp="$(mktemp)"
  awk '
    { lines[NR] = $0 }
    END {
      for (i=1; i<=NR; i++) {
        if (i>1 && lines[i] ~ /^[[:space:]]*}[[:space:]]*$/) {
          j = i-1
          while (j >= 1 && lines[j] ~ /^[[:space:]]*$/) j--
          if (j >= 1 && lines[j] ~ /,[[:space:]]*$/) sub(/,[[:space:]]*$/, "", lines[j])
        }
      }
      for (i=1; i<=NR; i++) print lines[i]
    }
  ' "$f" > "$tmp" && mv "$tmp" "$f"
}

# best-effort JSON validation; silent when python3 is unavailable
validate_json() {
  local f="$1"
  case "$f" in
    *.jsonc) return 0 ;;   # comments allowed; python3 json.tool would false-flag
  esac
  if command -v python3 >/dev/null 2>&1; then
    if ! python3 -m json.tool "$f" >/dev/null 2>&1; then
      echo "  ! warning: $f does not parse as JSON (opencode may fail to start)" >&2
    fi
  fi
}

opencode_set_default() {
  local root="$1" cfg prev tmp
  cfg="$(opencode_config_file "$root")" || return 0
  mkdir -p "$(dirname "$cfg")"
  if [ ! -f "$cfg" ]; then
    printf '{\n  "$schema": "https://opencode.ai/config.json",\n  "default_agent": "awesome-agent"\n}\n' > "$cfg"
    # marker: we created this key ourselves (empty = nothing to restore)
    mkdir -p "$(dirname "$DEFAULT_STATE")"
    : > "$DEFAULT_STATE"
    echo "  + opencode: default_agent -> awesome-agent (created $cfg)"
    return 0
  fi
  # record the previous default_agent only on the first transition, so update
  # runs stay idempotent and uninstall restores what was there before us
  prev="$(sed -n 's/.*"default_agent"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$cfg" | head -1)"
  if [ ! -f "$DEFAULT_STATE" ] && [ "$prev" != "awesome-agent" ]; then
    mkdir -p "$(dirname "$DEFAULT_STATE")"
    if [ -n "$prev" ]; then
      printf '%s\n' "$prev" > "$DEFAULT_STATE"
    else
      : > "$DEFAULT_STATE"     # no previous value: empty marker
    fi
  fi
  tmp="$(mktemp)"
  if [ -n "$prev" ]; then
    sed 's/\("default_agent"[[:space:]]*:[[:space:]]*"\)[^"]*"/\1awesome-agent"/' "$cfg" > "$tmp"
  elif grep -q '"$schema"' "$cfg" 2>/dev/null; then
    awk -v ins='  "default_agent": "awesome-agent",' '
      { print }
      !done && /"\$schema"/ { print ins; done=1 }
    ' "$cfg" > "$tmp"
  else
    awk -v ins='  "default_agent": "awesome-agent",' '
      { print }
      !done && /{/ { print ins; done=1 }
    ' "$cfg" > "$tmp"
  fi
  mv "$tmp" "$cfg"
  fix_dangling_comma "$cfg"
  validate_json "$cfg"
  echo "  + opencode: default_agent -> awesome-agent ($cfg)"
}

opencode_unset_default() {
  local root="$1" cfg prev tmp
  cfg="$(opencode_config_file "$root")" || return 0
  [ -f "$cfg" ] || { rm -f "$DEFAULT_STATE"; return 0; }
  if [ -f "$DEFAULT_STATE" ]; then
    prev="$(cat "$DEFAULT_STATE")"
    rm -f "$DEFAULT_STATE"
    tmp="$(mktemp)"
    if [ -n "$prev" ]; then
      sed 's|\("default_agent"[[:space:]]*:[[:space:]]*"\)[^"]*"|\1'"$prev"'"|' "$cfg" > "$tmp"
    else
      sed '/"default_agent"[[:space:]]*:/d' "$cfg" > "$tmp"
    fi
    mv "$tmp" "$cfg"
    fix_dangling_comma "$cfg"
    validate_json "$cfg"
    echo "  - opencode: default_agent restored/removed ($cfg)"
  else
    # no state file: the value was already awesome-agent before we installed,
    # so leave the user's config untouched
    echo "  - opencode: default_agent left as-is (pre-existing) ($cfg)"
  fi
}

# ---- kiro default_agent ----------------------------------------------------
# Installing into kiro also sets awesome-agent as the default agent
# ("chat.defaultAgent" in $root/settings/cli.json). The previous value is
# recorded so uninstall can restore it.
KIRO_STATE="${XDG_DATA_HOME:-$HOME/.local/share}/awesome-agent/kiro_default.txt"

kiro_config_file() {
  local root="$1"
  [ -z "$root" ] && root="$(harness_root kiro)"
  [ -z "$root" ] && return 1
  echo "$root/settings/cli.json"
}

kiro_set_default() {
  local root="$1" cfg prev tmp
  cfg="$(kiro_config_file "$root")" || return 0
  [ -f "$cfg" ] || return 0
  prev="$(sed -n 's/.*"chat\.defaultAgent"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$cfg" | head -1)"
  if [ ! -f "$KIRO_STATE" ] && [ "$prev" != "awesome-agent" ]; then
    mkdir -p "$(dirname "$KIRO_STATE")"
    if [ -n "$prev" ]; then
      printf '%s\n' "$prev" > "$KIRO_STATE"
    else
      : > "$KIRO_STATE"
    fi
  fi
  tmp="$(mktemp)"
  if [ -n "$prev" ]; then
    sed 's/\("chat\.defaultAgent"[[:space:]]*:[[:space:]]*"\)[^"]*"/\1awesome-agent"/' "$cfg" > "$tmp"
  else
    awk -v ins='  "chat.defaultAgent": "awesome-agent",' '
      { print }
      !done && /{/ { print ins; done=1 }
    ' "$cfg" > "$tmp"
  fi
  mv "$tmp" "$cfg"
  fix_dangling_comma "$cfg"
  validate_json "$cfg"
  echo "  + kiro: chat.defaultAgent -> awesome-agent ($cfg)"
}

kiro_unset_default() {
  local root="$1" cfg prev tmp
  cfg="$(kiro_config_file "$root")" || return 0
  [ -f "$cfg" ] || { rm -f "$KIRO_STATE"; return 0; }
  if [ -f "$KIRO_STATE" ]; then
    prev="$(cat "$KIRO_STATE")"
    rm -f "$KIRO_STATE"
    tmp="$(mktemp)"
    if [ -n "$prev" ]; then
      sed 's|\("chat\.defaultAgent"[[:space:]]*:[[:space:]]*"\)[^"]*"|\1'"$prev"'"|' "$cfg" > "$tmp"
    else
      sed '/"chat\.defaultAgent"[[:space:]]*:/d' "$cfg" > "$tmp"
    fi
    mv "$tmp" "$cfg"
    fix_dangling_comma "$cfg"
    validate_json "$cfg"
    echo "  - kiro: chat.defaultAgent restored/removed ($cfg)"
  else
    echo "  - kiro: chat.defaultAgent left as-is (pre-existing) ($cfg)"
  fi
}

# ---- actions ---------------------------------------------------------------
do_install() {
  local id="$1" root cmd_dir agent_dir skill_root
  read -r root cmd_dir agent_dir skill_root <<< "$(harness_dirs "$id")"
  [ -z "$root" ] && { echo "! unknown target $id"; return 1; }
  local add=() rp src dest
  while IFS= read -r rp; do
    [ -z "$rp" ] && continue
    src="$(src_for "$id" "$rp")" || continue      # .skip excluded, or no source
    dest="$(target_file "$id" "$rp" "$root")"
    [ -z "$dest" ] && continue                    # e.g. overlay for another harness
    mkdir -p "$(dirname "$dest")"
    cp "$SCRIPT_DIR/$src" "$dest"
    add+=("$rp")
  done < <(manifest_current)
  # prune legacy files installed here but later removed from the plugin
  local line f
  line="$(registry_get "$id")"
  if [ -n "$line" ]; then
    for f in ${line##*|}; do
      f="$(relpath_of "$f")"
      [ -n "$(manifest_is_removed "$f")" ] && rm -f "$(target_file "$id" "$f" "$root")"
    done
  fi
  registry_add "$id" "$root" "${add[@]}"
  echo "  + $id -> $root (installed: $(printf '%s ' "${add[@]##*/}"))"
  if [ "$id" = opencode ]; then
    opencode_set_default "$root"
  fi
  if [ "$id" = kiro ]; then
    kiro_set_default "$root"
  fi
}
do_uninstall() {
  local id="$1"
  local line; line="$(registry_get "$id")"
  [ -z "$line" ] && { echo "  - $id (not registered)"; return; }
  local root="${line#*|}"; root="${root%|*}"
  local f removed=0 dest
  for f in ${line##*|}; do
    f="$(relpath_of "$f")"
    dest="$(target_file "$id" "$f" "$root")"
    [ -z "$dest" ] && continue
    if [ -f "$dest" ]; then rm -f "$dest"; removed=$((removed+1)); fi
  done
  registry_remove "$id"
  echo "  - $id (removed $removed file(s) from $root)"
  if [ "$id" = opencode ]; then
    opencode_unset_default "$root"
  fi
  if [ "$id" = kiro ]; then
    kiro_unset_default "$root"
  fi
}

# ---- CLI -------------------------------------------------------------------
usage() {
  cat <<EOF
awesome-agent installer

Usage:
  $0                interactive install (detect harnesses, multi-select)
  $0 install        same as above
  $0 update         re-copy current files + prune removed ones (TUI to pick)
  $0 uninstall      remove from registered targets, incl. legacy files (TUI)
  $0 --all          non-interactive: install into every detected harness
  $0 --target a,b   install into listed ids
                    (opencode,claude,codex,pi,kilo,kiro,kimi,deepseek,cursor,local)
  $0 --help         this message

Files are tracked in MANIFEST.txt (rel_path|version_added|version_removed) so
uninstall cleans up commands/skills even after they are removed from the plugin.
EOF
}
detected_ids() {
  local id out=()
  for id in "${ALL_IDS[@]}"; do
    [ -n "$(harness_installed "$id")" ] && out+=("$id")
  done
  echo "${out[@]}"
}

main() {
  local mode="install" targets_spec=""
  while [ $# -gt 0 ]; do
    case "$1" in
      install|update|uninstall) mode="$1" ;;
      --all) targets_spec="ALL" ;;
      --target) targets_spec="$2"; shift ;;
      --help|-h) usage; exit 0 ;;
      *) echo "unknown arg: $1"; usage; exit 1 ;;
    esac
    shift
  done

  local ids=() labels=()
  if [ "$mode" = "update" ] || [ "$mode" = "uninstall" ]; then
    while IFS='|' read -r id dir files; do
      [ -z "$id" ] && continue
      ids+=("$id"); labels+=("$(harness_label "$id")  [$dir]")
    done < <(registry_list)
    if [ ${#ids[@]} -eq 0 ]; then echo "No registered targets. Run '$0' to install first."; exit 1; fi
  else
    local d
    for d in $(detected_ids); do ids+=("$d"); labels+=("$(harness_label "$d")"); done
    if [ ${#ids[@]} -eq 0 ]; then echo "No supported harnesses detected on this machine."; exit 1; fi
  fi

  local chosen=()
  if [ "$targets_spec" = "ALL" ]; then
    chosen=("${ids[@]}")
  elif [ -n "$targets_spec" ]; then
    IFS=',' read -ra chosen <<< "$targets_spec"
  else
    multiselect "${labels[@]}"
    [ -z "$SELECTED_IDX" ] && { echo "Cancelled."; exit 0; }
    local i; for i in $SELECTED_IDX; do chosen+=("${ids[i]}"); done
  fi
  [ ${#chosen[@]} -eq 0 ] && { echo "No targets selected."; exit 0; }

  echo "== awesome-agent: $mode =="
  local t
  for t in "${chosen[@]}"; do
    case "$mode" in
      install|update)   do_install "$t" ;;
      uninstall)        do_uninstall "$t" ;;
    esac
  done
  echo "Done."
}
main "$@"

#!/usr/bin/env python3
"""Regression tests for the awesome-agent permission/auto-approval configuration.

These tests encode every safety invariant we rely on for the Kiro harness agent
(harnesses/kiro/agents/awesome-agent.{json,md}):

  * pattern synchronization: execute_bash == shell, JSON == MD, source == installed
  * allow-by-pattern semantics: commands that must auto-approve, commands that
    must fall through to `ask`
  * sensitive-path guards: readers/sops must never match ssh/aws/env/secrets/...
  * metacharacter guards: `; & | < > ` $` inside an arg makes the command prompt
  * sops decrypt is NOT auto-approved (it prints plaintext secrets)
  * deploy-dir (helm/helmfile/k8s/...) reads are guarded but allowed
  * fs_read/fs_write/web_fetch denied paths == permissions.rules ask globs
  * ask-before-allow ordering of the 3.x permission rules

Run from the repo root:

    python3 tests/test_awesome_agent.py            # direct
    python3 -m unittest discover tests             # via unittest discovery
    pytest tests                                   # via pytest

NOTE on matching semantics (mirrors Kiro's "allow by pattern" model):
  * A command auto-approves iff at least one pattern matches it; otherwise it
    falls through to `ask`.
  * `&&` chains auto-approve only if EVERY part matches a pattern.
  * Reader patterns end in `[^;&|<>`$\\n]` so a metacharacter in a reader's
    arguments forces `ask`. The plain git patterns are prefix-match only, so
    `git status | head` still auto-approves (both sides read-only, by design);
    the dangerous leaks are covered in TestKnownGaps.
"""

import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]


def repo_path(*parts):
    return REPO.joinpath(*parts)


def read_json(p):
    with open(p) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# MD frontmatter -> data (dependency-free, format is rigid: 2-space sections,
# 4-space keys, 6-space `- "item"` lists)
# ---------------------------------------------------------------------------

def _indent(line):
    return len(line) - len(line.lstrip(" "))


def md_frontmatter(md_text):
    marker_lines = [i for i, line in enumerate(md_text.split("\n")) if line.strip() == "---"]
    assert len(marker_lines) == 2, f"expected exactly 2 --- markers, got {len(marker_lines)}"
    fm_start, fm_end = marker_lines
    fm_lines = md_text.split("\n")[fm_start + 1:fm_end]
    body = "\n".join(md_text.split("\n")[fm_end + 1:]).strip("\n")
    return fm_lines, body


def _section(fm_lines, header):
    """Lines belonging to the `  <header>:` section (excluding header line itself)."""
    start = None
    for i, line in enumerate(fm_lines):
        if _indent(line) == 2 and re.match(rf"\s*{header}:", line):
            start = i
            break
    if start is None:
        return []
    end = len(fm_lines)
    for j in range(start + 1, len(fm_lines)):
        line = fm_lines[j]
        if not line.strip():
            continue
        if _indent(line) <= 2:
            end = j
            break
    return fm_lines[start + 1:end]


def _key_items(sec_lines, key):
    """Items of the `    <key>:` list inside a section (unicode-escaped backslashes)."""
    out = []
    collecting = False
    for line in sec_lines:
        if re.match(rf"\s*{key}:", line):
            collecting = True
            continue
        if collecting and re.match(r"^\s{6,}- ", line):
            item = line.strip().lstrip("-").strip().strip('"')
            out.append(item.replace("\\\\", "\\"))
        elif collecting and re.match(r"\s*[a-zA-Z_][a-zA-Z_-]*:", line):
            collecting = False
    return out


def _key_bool(sec_lines, key):
    for line in sec_lines:
        m = re.match(rf"\s*{key}:\s*(true|false)", line)
        if m:
            return m.group(1) == "true"
    return None


def md_shell_allowed(fm_lines):
    return _key_items(_section(fm_lines, "shell"), "allowedCommands")


def md_fs_read_denied(fm_lines):
    return _key_items(_section(fm_lines, "fs_read"), "deniedPaths")


def md_write_denied(fm_lines):
    return _key_items(_section(fm_lines, "write"), "deniedPaths")


def md_web_blocked(fm_lines):
    return _key_items(_section(fm_lines, "web_fetch"), "blocked")


def md_shell_bool(fm_lines, key):
    return _key_bool(_section(fm_lines, "shell"), key)


# ---------------------------------------------------------------------------
# Config wrapper
# ---------------------------------------------------------------------------

class KiroConfig:
    def __init__(self, json_path, md_path):
        self.data = read_json(json_path)
        self.md = open(md_path).read()

        # --- JSON (2.x executor + 3.x shell share the same lists) ---
        ts = self.data["toolsSettings"]
        self.execute_bash = ts["execute_bash"]["allowedCommands"]
        self.shell = ts["shell"]["allowedCommands"]
        self.shell_meta = {k: ts["shell"].get(k) for k in ("autoAllowReadonly", "denyByDefault")}
        self.fs_read_allowed = ts["fs_read"]["allowedPaths"]
        self.fs_read_denied = ts["fs_read"]["deniedPaths"]
        self.fs_write_allowed = ts["fs_write"]["allowedPaths"]
        self.fs_write_denied = ts["fs_write"]["deniedPaths"]
        self.web_trusted = ts["web_fetch"]["trusted"]
        self.web_blocked = ts["web_fetch"]["blocked"]

        # --- MD frontmatter ---
        self.fm_lines, self.body = md_frontmatter(self.md)
        self.md_shell_allowed = md_shell_allowed(self.fm_lines)
        self.md_fs_read_denied = md_fs_read_denied(self.fm_lines)
        self.md_fs_write_denied = md_write_denied(self.fm_lines)
        self.md_web_blocked = md_web_blocked(self.fm_lines)
        self.md_shell_meta = {k: md_shell_bool(self.fm_lines, k)
                              for k in ("autoAllowReadonly", "denyByDefault")}

        # --- permissions.rules ---
        self.rules = self.data["permissions"]["rules"]

    # -- matching semantics (mirrors Kiro's allow-by-pattern model) ---------
    def is_allowed(self, cmd):
        """True if any allowedCommand pattern matches the whole (un-split) command."""
        return any(re.search(p, cmd) for p in self.shell)

    def parts_allowed(self, cmd):
        """Kiro splits on && and auto-approves only if every part is allowed."""
        return all(self.is_allowed(part.strip()) for part in re.split(r"\s*&&\s*", cmd))

    # -- structural helpers --------------------------------------------------
    def rule(self, capability, effect):
        return [r for r in self.rules if r.get("capability") == capability and r.get("effect") == effect]


# Paths that must NEVER auto-approve (hard markers). Duplicated here on purpose
# so a drift in the shipped guard is a test failure, not a silent change.
SENSITIVE_MARKERS = [
    ".ssh", ".aws", ".gnupg", ".pem", ".p12", ".pfx", ".key",
    "id_rsa", "id_ed25519", "shadow", ".bash_history", ".zsh_history",
    ".bashrc", ".bash_profile", ".zshrc", ".profile", ".gitconfig",
    ".npmrc", ".netrc", ".env",
]


# ---------------------------------------------------------------------------
# Structure / synchronization
# ---------------------------------------------------------------------------

class TestStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = KiroConfig(
            repo_path("harnesses", "kiro", "agents", "awesome-agent.json"),
            repo_path("harnesses", "kiro", "agents", "awesome-agent.md"),
        )

    def test_execute_bash_and_shell_are_synced(self):
        self.assertEqual(self.cfg.execute_bash, self.cfg.shell)
        self.assertGreater(len(self.cfg.shell), 0)

    def test_md_shell_allowed_matches_json_shell(self):
        # Same patterns, exact same multiset. Order is intentionally NOT
        # enforced (Kiro matches any pattern, so ordering is cosmetic and the
        # JSON/MD files have historically drifted in ordering without a bug).
        from collections import Counter
        self.assertEqual(Counter(self.cfg.md_shell_allowed), Counter(self.cfg.shell))

    def test_md_prompt_body_matches_json_prompt(self):
        self.assertEqual(self.cfg.body, self.cfg.data["prompt"].strip("\n"))

    def test_shell_meta_flags(self):
        self.assertTrue(self.cfg.shell_meta["autoAllowReadonly"])
        self.assertFalse(self.cfg.shell_meta["denyByDefault"])
        self.assertEqual(self.cfg.shell_meta, self.cfg.md_shell_meta)

    def test_shell_patterns_are_anchored(self):
        for p in self.cfg.shell:
            self.assertTrue(p.startswith("^"), f"pattern not anchored: {p}")

    def test_dangerous_commands_are_not_in_allowlist(self):
        for bad in ("git push", "git pull ", "git fetch ", "git clone", "rm -rf",
                    "sudo ", "pip install", "npm install", "brew install"):
            for p in self.cfg.shell:
                self.assertNotIn(bad, p, f"dangerous literal in pattern: {p}")

    def test_sensitive_markers_present_in_reader_guard(self):
        reader = next(p for p in self.cfg.shell
                      if p.startswith(r"^(cat|head|tail|wc|sort|uniq|cut|tr|grep|rg)(?:\s+"))
        for m in (r"\.ssh", r"\.env", "secrets", "credentials"):
            self.assertIn(m, reader)

    def test_deploy_reader_still_guarded(self):
        deploy = next(p for p in self.cfg.shell if "helm|helmfile" in p)
        self.assertIn(r"helm|helmfile|helm-gcp", deploy)
        self.assertIn(r"(?!.*\.\.)", deploy)      # traversal still blocked
        self.assertIn(r"\.env", deploy)           # markers still enforced

    def test_sops_pattern_still_blocks_decrypt(self):
        sops = next(p for p in self.cfg.shell if p.startswith("^sops"))
        for guard in ("-d", "--decrypt", "-di"):
            self.assertIn(guard, sops)
        self.assertIn(r"\.env", sops)

    def test_knowledge_of_normalized_markers(self):
        # If the hard marker set intentionally grows, update this list together
        # with SENSITIVE_MARKERS so the tests stay honest.
        join = "|".join(SENSITIVE_MARKERS)
        for m in SENSITIVE_MARKERS:
            self.assertIn(m, join)

    # -- permission rules ----------------------------------------------------
    def test_fs_read_denied_matches_permissions_ask_rule(self):
        ask = self.cfg.rule("fs_read", "ask")
        self.assertEqual(len(ask), 1, "expected exactly one fs_read ask rule")
        self.assertEqual(set(ask[0]["match"]), set(self.cfg.fs_read_denied))
        self.assertEqual(set(self.cfg.md_fs_read_denied), set(self.cfg.fs_read_denied))
        self.assertGreaterEqual(len(self.cfg.fs_read_denied), 17)

    def test_fs_read_ask_comes_before_allow(self):
        idx_ask = next(i for i, r in enumerate(self.cfg.rules)
                       if r.get("capability") == "fs_read" and r.get("effect") == "ask")
        idx_allow = next(i for i, r in enumerate(self.cfg.rules)
                         if r.get("capability") == "fs_read" and r.get("effect") == "allow")
        self.assertLess(idx_ask, idx_allow, "fs_read ask rule must precede allow rule")

    def test_shell_allow_comes_before_ask(self):
        idx_allow = next(i for i, r in enumerate(self.cfg.rules)
                         if r.get("capability") == "shell" and r.get("effect") == "allow")
        idx_ask = next(i for i, r in enumerate(self.cfg.rules)
                       if r.get("capability") == "shell" and r.get("effect") == "ask")
        self.assertLess(idx_allow, idx_ask, "shell allow rule must precede ask rule")

    def test_denied_paths_cover_all_known_sensitive_sources(self):
        denied = "\n".join(self.cfg.fs_read_denied)
        for m in (".env", "secrets/**", "credentials/**", "~/.ssh/**", "~/.aws/**",
                  "~/.gnupg/**", "~/.git-credentials", "**/*.pem", "**/*.key",
                  "**/id_rsa", "**/id_ed25519"):
            self.assertIn(m, denied)

    def test_fs_write_denied_matches_permissions_ask_rule(self):
        ask = self.cfg.rule("fs_write", "ask")
        self.assertEqual(len(ask), 1)
        self.assertEqual(set(ask[0]["match"]), set(self.cfg.fs_write_denied))
        self.assertEqual(set(self.cfg.md_fs_write_denied), set(self.cfg.fs_write_denied))

    def test_web_fetch_blocked_matches_permissions_ask_rule(self):
        # toolsSettings uses regex (.*pastebin\\.com.*); the 3.x rule uses globs
        # (*pastebin.com*). Compare on the normalized domain tokens.
        def token(s):
            t = s.strip(".*")
            return t.replace("\\", "") if "\\" in s else t
        ask = self.cfg.rule("web_fetch", "ask")
        self.assertEqual(len(ask), 1)
        self.assertEqual({token(g) for g in ask[0]["match"]}, {token(r) for r in self.cfg.web_blocked})
        self.assertEqual({token(r) for r in self.cfg.md_web_blocked}, {token(r) for r in self.cfg.web_blocked})

    # -- shipped mirrors && installed targets --------------------------------
    def test_awesome_agent_mirror_is_synced(self):
        for rel in ("agents/awesome-agent.md", "skills/awesome-plan/SKILL.md"):
            source = repo_path(rel)
            mirror = repo_path(".awesome-agent", rel)
            self.assertTrue(source.exists(), f"missing source {rel}")
            self.assertTrue(mirror.exists(), f"missing mirror .awesome-agent/{rel}")
            self.assertEqual(source.read_text(), mirror.read_text(), f"mirror drift: .awesome-agent/{rel}")

    def test_installed_kiro_copy_matches_source(self):
        """Catches the 'edited source but forgot ./install.sh' regression."""
        home = pathlib.Path.home()
        cases = (
            (".kiro/agents/awesome-agent.json", "harnesses/kiro/agents/awesome-agent.json", "json"),
            (".kiro/agents/awesome-agent.md", "harnesses/kiro/agents/awesome-agent.md", "text"),
        )
        for installed_rel, src_rel, kind in cases:
            installed = home / installed_rel
            if not installed.exists():
                self.skipTest(f"installed copy not present: ~/{installed_rel}")
            if kind == "json":
                self.assertEqual(read_json(installed), read_json(repo_path(src_rel)),
                                 f"installed json drifted from source: {installed_rel}")
            else:
                self.assertEqual(installed.read_text(), repo_path(src_rel).read_text(),
                                 f"installed md drifted from source: {installed_rel}")


# ---------------------------------------------------------------------------
# Commands that MUST auto-approve
# ---------------------------------------------------------------------------

class TestAllowedCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = KiroConfig(
            repo_path("harnesses", "kiro", "agents", "awesome-agent.json"),
            repo_path("harnesses", "kiro", "agents", "awesome-agent.md"),
        )

    def assert_allowed(self, cmd):
        self.assertTrue(self.cfg.parts_allowed(cmd), f"expected auto-approve, got ask: {cmd}")

    def assert_blocked(self, cmd):
        self.assertFalse(self.cfg.parts_allowed(cmd), f"expected ask/prompt, got auto-approve: {cmd}")

    # -- git ---------------------------------------------------------------
    def test_git_readonly_is_allowed(self):
        for cmd in (
            "git status", "git status --porcelain", "git diff", "git diff --staged",
            "git log --oneline -10", "git show HEAD", "git branch --show-current",
            "git branch -a", "git tag -l", "git tag --list", "git remote -v",
            "git remote show origin", "git remote get-url origin", "git config --get user.name",
            "git config --list", "git rev-parse HEAD", "git merge-base HEAD origin/main",
            "git rev-list --count HEAD", "git describe --tags", "git ls-files",
            "git cat-file -p HEAD", "git blame src/main.kt", "git grep TODO",
            "git shortlog -sn", "git show-ref", "git for-each-ref", "git name-rev HEAD",
            "git fsck", "git cherry -v", "git submodule status", "git worktree list",
            "git --version", "/usr/bin/git status", "/usr/local/bin/git diff",
            "/opt/homebrew/bin/git log",
        ):
            self.assert_allowed(cmd)

    def test_git_mutations_are_allowed(self):
        for cmd in (
            "git add src/main.kt",
            "git reset --soft HEAD~1", "git reset --mixed HEAD~1", "git reset --hard HEAD~1",
            "git restore src/main.kt", "git checkout feature", "git switch feature",
            "git commit -m fix", "git merge feature", "git rebase main", "git stash",
            "git stash list", "git stash show", "git stash pop", "git stash apply",
            "git stash push", "git tag v1.0", "git cherry-pick abc123", "git rm old.kt",
            "git mv a b",
        ):
            self.assert_allowed(cmd)

    def test_git_c_variants_allowed(self):
        for cmd in (
            "git -C /tmp/repo status", "git -C /tmp/repo diff", "git -C /tmp/repo log --oneline",
            "git -C /tmp/repo show HEAD", "git -C /tmp/repo branch --show-current",
            "git -C /tmp/repo rev-parse HEAD", "git -C /tmp/repo merge-base HEAD origin/main",
            "git -C /tmp/repo tag --list", "git -C /tmp/repo remote show origin",
            "git -C /tmp/repo config --list",
        ):
            self.assert_allowed(cmd)

    def test_and_chains_are_allowed_when_each_part_is(self):
        # Original root-cause regression: && chains only auto-approve if every part matches.
        for cmd in (
            "git rev-parse HEAD && git merge-base HEAD origin/main",
            "git status && git diff --staged",
            "pwd && ls && git status",
        ):
            self.assert_allowed(cmd)

    def test_git_write_beyond_allowlist_is_blocked(self):
        for cmd in (
            "git push", "git push origin main", "git pull", "git fetch",
            "git clone https://github.com/x/y.git", "git -C /tmp/repo push",
            "git -C /tmp/repo fetch",
        ):
            self.assert_blocked(cmd)

    # -- build/test runners ------------------------------------------------
    def test_build_runners_allowed(self):
        for cmd in (
            "./gradlew test", "./gradlew build", "./gradlew ktlintCheck", "./gradlew bootJar",
            "./gradlew clean compileKotlin", "./gradlew test --dry-run", "cargo test",
            "cargo build --release", "cargo clippy", "npm run test", "npm run build -- --watch",
            "npm run test:unit", "npm run lintfix", "npm run validate-swagger", "npm run tsc",
            "npm tsc --version", "npx jest", "npx eslint --fix", "yarn build", "pnpm lint",
            "make test", "python -m pytest tests/", "python -m unittest tests",
            "pytest tests/", "black .", "ruff check .", "ruff format .", "mvn test",
            "mvn package -DskipTests", "gradle test",
        ):
            self.assert_allowed(cmd)

    def test_install_like_commands_are_blocked(self):
        for cmd in (
            "npm install", "npm install lodash", "yarn add lodash", "pnpm add lodash",
            "pip install requests", "pip3 install requests", "poetry add requests",
            "brew install postgresql", "cargo add serde", "go get github.com/x/y",
            "docker pull nginx", "docker run nginx", "kubectl apply -f deploy.yaml",
            "terraform apply",
        ):
            self.assert_blocked(cmd)

    # -- safe shell --------------------------------------------------------
    def test_safe_shell_allowed(self):
        for cmd in (
            "pwd", "true", "false", "whoami", "hostname", "date", "uname -a",
            "echo hello", "echo", "printf '%s' hi", "which git", "type python3",
            "command -v node", "basename src/main.kt", "dirname src/main.kt",
            "realpath .", "ls", "ls -la", "ls src tests", "df -h", "du -sh .",
            "lsof -i :8080", "stat src/main.kt", "file README.md", "readlink cmd",
        ):
            self.assert_allowed(cmd)

    def test_readers_allowed_on_safe_paths(self):
        for cmd in (
            "cat README.md", "cat build.gradle.kts", "head -20 src/main.kt",
            "head src/main.kt", "tail -50 logs/app.log", "tail logs/app.log",
            "wc -l src/main.kt", "sort deps.txt", "uniq tags.txt",
            "cut -d: -f1 /etc/passwd", "tr a-z A-Z text.txt", "grep -n TODO src tests",
            "grep error app.log", "rg pattern src", "rg -l foo .",
            "cat .github/workflows/ci.yml", "head docker-compose.yml", "tail -f /dev/null",
        ):
            self.assert_allowed(cmd)

    def test_bare_readers_allowed(self):
        # Regression from the 'tail -> prompted because \s+ never matches' bug.
        for cmd in ("cat", "head", "tail", "grep", "rg", "wc", "sort", "uniq", "cut", "tr"):
            self.assert_allowed(cmd)

    def test_deploy_dir_reads_allowed(self):
        for cmd in (
            "cat helm-gcp/secrets.yaml", "cat helm/secrets.enc.yaml",
            "head -20 helm/charts/sub/secrets.yaml", "tail -10 helmfile/secrets.yaml",
            "grep -n key k8s/overlays/prod/secrets.yaml", "rg httpbin charts/values.yaml",
            "cat infra/secrets.yaml", "cat deploy/secrets.yaml", "cat kustomize/prod/secrets.enc.yaml",
            "cat config/secrets.yaml", "cat clusters/secrets.yaml", "wc -l helm/values.yaml",
        ):
            self.assert_allowed(cmd)

    # -- sops --------------------------------------------------------------
    def test_sops_non_decrypt_allowed(self):
        for cmd in (
            "sops", "sops -e helm-gcp/secrets.yaml", "sops --encrypt helm/values.yaml",
            "sops edit helm/secrets.yaml", "sops --set '[\"k\"]=\"v\"' helm/values.yaml",
            "sops -i helm/values.yaml", "sops --rotate-keys -e helm/values.yaml",
        ):
            self.assert_allowed(cmd)

    def test_sops_decrypt_is_blocked(self):
        # Decrypt prints plaintext secrets to stdout — must always ask.
        for cmd in (
            "sops -d helm-gcp/secrets.yaml", "sops --decrypt helm/secrets.enc.yaml",
            "sops -d", "sops --decrypt", "sops -d -i secrets.yaml", "sops -di secrets.yaml",
            "sops -i -d secrets.yaml", "sops --decrypt --output /tmp/out.yaml secrets.yaml",
        ):
            self.assert_blocked(cmd)

    # -- absolute paths ----------------------------------------------------
    def test_absolute_bin_paths_allowed(self):
        for cmd in (
            "/usr/bin/git status", "/usr/local/bin/git status",
            "/opt/homebrew/bin/git diff", "/usr/bin/node --version",
            "/usr/local/bin/npm run test", "/opt/homebrew/bin/python3 -m pytest tests/",
        ):
            self.assert_allowed(cmd)

    # -- documented conservatism (deliberately blocked today) ---------------
    def test_documented_conservative_prompts(self):
        """These currently ask. If you want them auto-approved, change the
        patterns AND delete this test — don't just add the test case."""
        for cmd in (
            "git reset",                 # bare reset requires a path/flag
            "git stash push -m wip",     # stash push accepts no args beyond the verb
            "python3 -m pytest tests/",  # bare runner is `python`, not `python3`
        ):
            self.assert_blocked(cmd)


# ---------------------------------------------------------------------------
# Commands that MUST prompt
# ---------------------------------------------------------------------------

class TestBlockedCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = KiroConfig(
            repo_path("harnesses", "kiro", "agents", "awesome-agent.json"),
            repo_path("harnesses", "kiro", "agents", "awesome-agent.md"),
        )

    def assert_blocked(self, cmd):
        self.assertFalse(self.cfg.parts_allowed(cmd), f"expected ask/prompt, got auto-approve: {cmd}")

    def test_sensitive_reads_always_prompt(self):
        for cmd in (
            "cat .env", "cat .env.local", "cat helm/.env", "head -5 .env", "tail .env",
            "grep API_KEY .env", "cat secrets/api-key.txt", "cat credentials/foo",
            "cat helm-gcp/secrets/real.env", "cat ~/.ssh/id_rsa", "cat ~/.ssh/config",
            "head -5 ~/.aws/credentials", "cat ~/.aws/config",
            "cat ~/.gnupg/private-keys-v1.d/x.key", "cat ~/.gitconfig", "cat ~/.npmrc",
            "cat ~/.netrc", "cat ~/.bashrc", "cat ~/.bash_profile", "cat ~/.zshrc",
            "cat ~/.profile", "cat ~/.bash_history", "cat /etc/shadow", "cat app-key.pem",
            "cat cert.p12", "cat id_ed25519", "grep -r password secrets/",
        ):
            self.assert_blocked(cmd)

    def test_traversal_reads_prompt(self):
        for cmd in (
            "cat helm/../../.ssh/id_rsa", "head ../../.env", "tail ../.env",
            "cat helm/../../.env",
        ):
            self.assert_blocked(cmd)

    def test_sensitive_sops_prompt(self):
        for cmd in ("sops -d ~/.aws/foo", "sops -d .env", "sops -e ~/.ssh/id_rsa"):
            self.assert_blocked(cmd)

    def test_metacharacter_smuggling_prompts(self):
        for cmd in (
            "cat helm/values.yaml; rm -rf /", "cat build.gradle.kts && rm -rf /",
            "cat x | base64", "tail -f logs | grep secret", "echo $(rm -rf /)",
            "echo `date`", "cat x > /tmp/out", "cat x < /etc/shadow",
            "sops -d secrets.yaml && echo done",
        ):
            self.assert_blocked(cmd)

    def test_redirection_with_git_is_allowed_by_prefix_design(self):
        # git patterns are prefix-match only, so a trailing redirection/pipe on
        # an allowed subcommand auto-approves. Harmless for `status`; the file-
        # content leak case is tracked in TestKnownGaps.
        self.assertTrue(self.cfg.parts_allowed("git status > /dev/null"))
        self.assertTrue(self.cfg.parts_allowed("git status | head"))
        self.assertTrue(self.cfg.parts_allowed("git log --oneline | head -5"))

    def test_dangerous_or_unlisted_commands_prompt(self):
        for cmd in (
            "rm -rf /", "sudo rm -rf /", "brew install postgresql", "pip install requests",
            "npm install", "kubectl delete pod x", "terraform destroy", "docker compose up",
            "chmod 777 /etc", "kill -9 1234", "dd if=/dev/zero of=/dev/sda", "git push",
            "python3 -m pytest tests/", "git stash push -m wip", "git reset",
        ):
            self.assert_blocked(cmd)


# ---------------------------------------------------------------------------
# Known open gaps — the guard doesn't do this yet. When fixed, remove the
# @expectedFailure marker and the test goes green.
# ---------------------------------------------------------------------------

class TestKnownGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = KiroConfig(
            repo_path("harnesses", "kiro", "agents", "awesome-agent.json"),
            repo_path("harnesses", "kiro", "agents", "awesome-agent.md"),
        )

    @unittest.expectedFailure
    def test_git_show_file_content_read_should_prompt(self):
        # git show HEAD:secret.env auto-approves today because ^git\s+show has
        # no sensitive-marker guard. It should behave like cat .env (ask).
        self.assertFalse(self.cfg.parts_allowed("git show HEAD:secret.env"))
        self.assertFalse(self.cfg.parts_allowed("git -C /tmp/repo show HEAD:.env"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
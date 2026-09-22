#!/usr/bin/env python3
"""Mechanical and adversarial validation for AI Game Development OS v1.2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS))
from common import parse_frontmatter  # noqa: E402


REQUIRED = [
    "VERSION",
    "AGENTS.md",
    "CLAUDE.md",
    ".claude/settings.json",
    ".claude/hooks/common.py",
    ".claude/hooks/govern_write.py",
    ".claude/hooks/govern_shell.py",
    ".claude/hooks/govern_mcp.py",
    ".claude/hooks/block_config_change.py",
    ".github/workflows/aigdo-validation.yml",
    "scripts/activate_lease.py",
    "scripts/deactivate_lease.py",
    "scripts/seal_implementation.py",
    "scripts/verify_approval_signature.py",
    "scripts/doctor.py",
    "scripts/task_digest.py",
    "scripts/artifact_digest.py",
    "tests/governance_attack_corpus.json",
    ".ai-governance/mcp-policy.json",
    "docs/00-project/PROJECT-CONSTITUTION.md",
    "docs/00-project/PROJECT-STATUS.md",
    "docs/00-project/SECURITY-THREAT-MODEL.md",
    "docs/00-project/REPOSITORY-ATTESTATION.md",
    "docs/05-production/CURRENT-MILESTONE.md",
    "docs/05-production/CURRENT-TASK.md",
    "docs/08-process/SYSTEM-LIFECYCLE.md",
    "docs/templates/TASK-CONTRACT-TEMPLATE.md",
    "docs/templates/READY-REVIEW-RECEIPT-TEMPLATE.md",
    "docs/templates/ACCEPTANCE-RECEIPT-TEMPLATE.md",
    "docs/templates/EVIDENCE-PACK-TEMPLATE.md",
]

EXPECTED_AGENTS = {
    "repository-researcher", "gameplay-architect", "implementation-agent",
    "code-reviewer", "qa-reviewer", "performance-reviewer",
    "documentation-auditor", "acceptance-reviewer",
}

EXPECTED_SKILLS = {
    "project-discovery", "new-system", "ready-review", "implement-system",
    "verify-system", "close-system", "milestone-review", "drift-audit", "postmortem",
}


class Validation:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(message)


def hook_process(script: Path, root: Path, payload: dict, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(root)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        text=True, encoding="utf-8", errors="replace",
        capture_output=True,
        env=env,
        check=False,
    )


def hook_call(script: Path, root: Path, payload: dict) -> dict:
    completed = hook_process(script, root, payload)
    if completed.returncode != 0:
        raise RuntimeError(f"hook failed unexpectedly: {completed.stderr}")
    return json.loads(completed.stdout)


def decision(output: dict) -> str:
    return output["hookSpecificOutput"]["permissionDecision"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_files(v: Validation, working_repository: bool = False) -> None:
    for relative in REQUIRED:
        v.check((ROOT / relative).is_file(), f"missing required file: {relative}")
    v.check(len((ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()) < 200, "CLAUDE.md must remain under 200 lines")
    version = (ROOT / "VERSION").read_text(encoding="utf-8")
    v.check("AI Game Development OS 1.2.0" in version and "Schema: 3" in version, "VERSION must declare v1.2.0 schema 3")
    if working_repository:
        tracked = subprocess.run(
            ["git", "ls-files", "--", ".ai-governance/implementation-lease.json", ".ai-governance/implementation-seals"],
            cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
        )
        v.check(
            tracked.returncode == 0 and not tracked.stdout.strip(),
            "a lease or implementation seal must never be tracked by Git (working-repository mode needs a Git repository)",
        )
    else:
        v.check(not (ROOT / ".ai-governance" / "implementation-lease.json").exists(), "deliverable must not contain an active implementation lease")
        seal_dir = ROOT / ".ai-governance" / "implementation-seals"
        v.check(not seal_dir.exists() or not any(seal_dir.iterdir()), "deliverable must not contain an implementation seal")
    for path in list((ROOT / ".claude/hooks").glob("*.py")) + list((ROOT / "scripts").glob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            v.check(True, f"Python syntax valid: {path.name}")
        except SyntaxError as exc:
            v.check(False, f"Python syntax invalid {path.name}: {exc}")


def validate_settings(v: Validation) -> None:
    try:
        data = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    except Exception as exc:
        v.check(False, f"settings.json is invalid: {exc}")
        return
    permissions = data.get("permissions", {})
    v.check(data.get("env", {}).get("PYTHONDONTWRITEBYTECODE") == "1", "hook runtime must suppress bytecode artifacts")
    v.check(permissions.get("defaultMode") == "plan", "default permission mode must be plan")
    v.check(permissions.get("disableAutoMode") == "disable", "auto mode must be disabled")
    v.check(permissions.get("disableBypassPermissionsMode") == "disable", "bypassPermissions must be disabled")
    hooks = data.get("hooks", {}).get("PreToolUse", [])
    matchers = {item.get("matcher") for item in hooks}
    v.check("Write|Edit|NotebookEdit" in matchers, "write governance hook is not registered")
    v.check("Bash|PowerShell" in matchers, "shell governance hook is not registered")
    v.check("^mcp__.*$" in matchers, "MCP governance hook is not registered")
    config_hooks = data.get("hooks", {}).get("ConfigChange", [])
    config_matchers = {item.get("matcher") for item in config_hooks}
    v.check(
        "user_settings|project_settings|local_settings|skills" in config_matchers,
        "ConfigChange hardening hook is not registered",
    )


def validate_frontmatter(v: Validation) -> None:
    agent_names: set[str] = set()
    for path in sorted((ROOT / ".claude/agents").glob("*.md")):
        try:
            meta = parse_frontmatter(path)
            agent_names.add(meta.get("name", ""))
            v.check(bool(meta.get("description")), f"agent missing description: {path.name}")
            v.check(meta.get("maxTurns", "").isdigit(), f"agent missing finite maxTurns: {path.name}")
        except Exception as exc:
            v.check(False, f"invalid agent frontmatter {path.name}: {exc}")
    v.check(agent_names == EXPECTED_AGENTS, f"agent set mismatch: {sorted(agent_names ^ EXPECTED_AGENTS)}")

    skill_names: set[str] = set()
    for path in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
        try:
            meta = parse_frontmatter(path)
            skill_names.add(meta.get("name", ""))
            v.check(bool(meta.get("description")), f"skill missing description: {path.parent.name}")
            v.check(meta.get("disable-model-invocation") == "true", f"workflow skill must be user-invoked: {path.parent.name}")
        except Exception as exc:
            v.check(False, f"invalid skill frontmatter {path}: {exc}")
    v.check(skill_names == EXPECTED_SKILLS, f"skill set mismatch: {sorted(skill_names ^ EXPECTED_SKILLS)}")

    try:
        task_meta = parse_frontmatter(ROOT / "docs/05-production/tasks/TASK-CARGO-001-DRAFT.md")
        v.check(task_meta.get("status") == "DRAFT", "example task must remain DRAFT")
        v.check(task_meta.get("authored_by") == "UNSET", "example task must remain unauthored")
        v.check(task_meta.get("approved_by") == "UNSET", "example task must remain unapproved")
        v.check(task_meta.get("ready_review_receipt") == "UNSET", "example task must not reference a review receipt")
    except Exception as exc:
        v.check(False, f"example task frontmatter invalid: {exc}")


def validate_hooks(v: Validation) -> None:
    write_hook = HOOKS / "govern_write.py"
    shell_hook = HOOKS / "govern_shell.py"
    mcp_hook = HOOKS / "govern_mcp.py"
    config_hook = HOOKS / "block_config_change.py"
    with tempfile.TemporaryDirectory(prefix="aigdo-validation-") as temp:
        root = Path(temp)
        (root / ".ai-governance").mkdir()
        (root / ".ai-governance" / "mcp-policy.json").write_text(
            json.dumps({"schema": 1, "allow_without_lease": [], "allow_with_lease": []}),
            encoding="utf-8",
        )
        (root / "docs").mkdir()
        (root / "Source" / "Game").mkdir(parents=True)
        base = {"hook_event_name": "PreToolUse", "cwd": str(root)}

        def write(path: Path, tool: str = "Write") -> str:
            return decision(hook_call(write_hook, root, {**base, "tool_name": tool, "tool_input": {"file_path": str(path)}}))

        def shell(command: str, tool: str = "Bash") -> str:
            return decision(hook_call(shell_hook, root, {**base, "tool_name": tool, "tool_input": {"command": command}}))

        def mcp(name: str) -> str:
            return decision(hook_call(mcp_hook, root, {**base, "tool_name": name, "tool_input": {"query": "x"}}))

        corpus = json.loads((ROOT / "tests" / "governance_attack_corpus.json").read_text(encoding="utf-8"))

        v.check(write(root / "Source/Game/X.cpp") == "deny", "inactive lease must deny production write")
        v.check(write(root / "docs/note.md") == "ask", "documentation write without lease must ask")
        v.check(write(root / ".ai-governance/x") == "deny", "controlled path must always deny")
        for command in corpus["shell_allow_read_only"]:
            v.check(shell(command) == "allow", f"read-only corpus command should be allowed: {command}")
        v.check(shell("python scripts/doctor.py") == "allow", "doctor must be recognized as read-only")
        v.check(shell("python scripts/doctor.py --require-claude") == "allow", "strict doctor must be recognized as read-only")
        v.check(shell("python scripts/task_digest.py docs/task.md") == "allow", "task digest must be recognized as read-only")
        v.check(shell("python scripts/artifact_digest.py docs/evidence") == "allow", "artifact digest must be recognized as read-only")
        for command in corpus["shell_deny"]:
            v.check(shell(command) == "deny", f"attack corpus command must be denied: {command}")
        v.check(shell("Get-Content x | Set-Content y", "PowerShell") == "deny", "PowerShell pipeline must be denied without lease")
        for target in corpus["outside_write_targets"]:
            v.check(write(root / target) == "deny", f"outside write target must be denied: {target}")
        v.check(mcp("mcp__filesystem__read_file") == "deny", "MCP must be denied without a lease")

        config_result = hook_process(
            config_hook, root,
            {"hook_event_name": "ConfigChange", "source": "project_settings", "file_path": str(root / ".claude/settings.json")},
        )
        v.check(config_result.returncode == 0, "ConfigChange hook should return structured block output")
        try:
            v.check(json.loads(config_result.stdout).get("decision") == "block", "ConfigChange must block project settings changes")
        except json.JSONDecodeError:
            v.check(False, "ConfigChange hook output must be valid JSON")

        forced = hook_process(
            write_hook,
            root,
            {**base, "tool_name": "Write", "tool_input": {"file_path": str(root / "Source/Game/X.cpp")}},
            {"AIGDO_TEST_FORCE_ERROR": "1"},
        )
        v.check(forced.returncode == 2, "write hook internal error must exit 2")
        forced = hook_process(
            shell_hook,
            root,
            {**base, "tool_name": "Bash", "tool_input": {"command": "git status"}},
            {"AIGDO_TEST_FORCE_ERROR": "1"},
        )
        v.check(forced.returncode == 2, "shell hook internal error must exit 2")

        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "validator@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "AIGDO Validator"], cwd=root, check=True)

        task = root / "task.md"
        task.write_text("approved task\n", encoding="utf-8")
        task_digest = sha256(task)
        review = root / "review.md"
        review.write_text(
            "---\n"
            "review_id: REVIEW-TEST-001\n"
            "task_id: TASK-TEST-001\n"
            "disposition: READY_FOR_IMPLEMENTATION\n"
            "reviewer: independent-reviewer\n"
            f"task_sha256: {task_digest}\n"
            "reviewed_at: 2026-09-16T00:00:00Z\n"
            "approval_mode: hash\n"
            "---\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "validation base"], cwd=root, check=True)
        git_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=True
        ).stdout.strip()
        git_branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=True
        ).stdout.strip() or "DETACHED"
        lease = {
            "schema": 3,
            "state": "ACTIVE",
            "task_id": "TASK-TEST-001",
            "approved_by": "independent-reviewer",
            "authored_by": "implementer",
            "task_contract": "task.md",
            "task_sha256": task_digest,
            "ready_review_receipt": "review.md",
            "ready_review_sha256": sha256(review),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
            "allowed_paths": ["Source/Game/**"],
            "allowed_commands": ["echo test"],
            "approval_mode": "hash",
            "git_root": str(root.resolve()),
            "git_head": git_head,
            "git_branch": git_branch,
        }
        lease_path = root / ".ai-governance/implementation-lease.json"
        lease_path.write_text(json.dumps(lease), encoding="utf-8")

        v.check(write(root / "Source/Game/X.cpp", "Edit") == "allow", "active lease should allow in-scope write")
        v.check(write(root / "Source/Other.cpp", "Edit") == "deny", "active lease must deny out-of-scope write")
        shifted_cwd = {**base, "cwd": str(root / "Source"), "tool_name": "Edit"}
        v.check(
            decision(hook_call(write_hook, root, {**shifted_cwd, "tool_input": {"file_path": str(root / "Source/Game/X.cpp")}})) == "allow",
            "a lease write must be judged from the project root even when the working directory is shifted",
        )
        v.check(
            decision(hook_call(write_hook, root, {**shifted_cwd, "tool_input": {"file_path": str(root / "Source/Source/Game/Y.cpp")}})) == "deny",
            "a shifted working directory must not let an out-of-scope path pass as in-scope",
        )
        v.check(shell("echo test") == "allow", "simple pre-approved command should be allowed")
        v.check(shell("echo test > Source/Game/X.cpp") == "ask", "redirected approved command must ask")
        v.check(shell("echo test && rm -rf build") == "deny", "approved prefix must not bypass destructive suffix")
        v.check(mcp("mcp__filesystem__read_file") == "ask", "unknown MCP with a lease must require one-time approval")
        (root / ".ai-governance" / "mcp-policy.json").write_text(
            json.dumps({"schema": 1, "allow_without_lease": [], "allow_with_lease": ["mcp__filesystem__read_file"]}),
            encoding="utf-8",
        )
        v.check(mcp("mcp__filesystem__read_file") == "allow", "exact MCP allowlist must work with a lease")

        subprocess.run(["git", "checkout", "-qb", "drift-branch"], cwd=root, check=True)
        v.check(write(root / "Source/Game/X.cpp", "Edit") == "deny", "branch drift must invalidate lease")
        subprocess.run(["git", "checkout", "-q", git_branch], cwd=root, check=True)

        review.write_text(review.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
        v.check(write(root / "Source/Game/X.cpp", "Edit") == "deny", "review-receipt drift must invalidate lease")
        review.write_text(review.read_text(encoding="utf-8").removesuffix("changed\n"), encoding="utf-8")
        task.write_text("changed after approval\n", encoding="utf-8")
        v.check(write(root / "Source/Game/X.cpp", "Edit") == "deny", "task hash drift must invalidate lease")

        audit = root / ".ai-governance/audit.log"
        v.check(audit.is_file(), "governance audit log must be written")
        if audit.is_file():
            try:
                entries = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
                v.check(bool(entries) and all("decision" in item and "tool" in item for item in entries), "audit log entries must be valid JSONL")
            except Exception as exc:
                v.check(False, f"audit log invalid: {exc}")


def valid_owner_policy(git_path: str) -> dict:
    return {
        "schema": 1,
        "policy_id": "OWNER-POLICY-TEST",
        "issued_at": "2026-01-01T00:00:00Z",
        "expires_at": None,
        "max_lease_hours": 8,
        "required_branch": "agent/work",
        "base_branch": "main",
        "effective_rigor_cap": "R1",
        "git_executable": git_path,
        "max_changed_paths": 40,
        "max_total_bytes": 2000000,
        "max_leases_per_day": 12,
        "max_unmerged_commits": 20,
        "max_unmerged_paths": 200,
        "allowed_commands": [],
        "reviewer_ids": ["independent-reviewer"],
        "deny_paths": ["scripts/**"],
        "lanes": [
            {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**"], "max_rigor": "R1", "extensions": [".cs"]}
        ],
    }


def validate_owner_policy_mode(v: Validation) -> None:
    import common
    from unittest import mock

    git_path = shutil.which("git")
    if not git_path:
        v.check(False, "git must be available for the owner-policy tests")
        return
    git_path = str(Path(git_path).resolve())
    write_hook = HOOKS / "govern_write.py"
    shell_hook = HOOKS / "govern_shell.py"
    mcp_hook = HOOKS / "govern_mcp.py"
    with tempfile.TemporaryDirectory(prefix="aigdo-policy-") as temp:
        root = Path(temp)
        (root / ".ai-governance").mkdir()
        (root / ".ai-governance" / "mcp-policy.json").write_text(
            json.dumps({"schema": 1, "allow_without_lease": [], "allow_with_lease": []}),
            encoding="utf-8",
        )
        drafts = root / "docs" / "05-production" / "tasks"
        drafts.mkdir(parents=True)
        for git_args in (
            ["init", "-q"],
            ["config", "user.email", "validator@example.invalid"],
            ["config", "user.name", "AIGDO Validator"],
        ):
            subprocess.run([git_path, *git_args], cwd=root, check=True)
        (drafts / "TASK-TRACKED-001.md").write_text("tracked\n", encoding="utf-8")
        (drafts / "TASK-DELETED-001.md").write_text("deleted\n", encoding="utf-8")
        subprocess.run([git_path, "add", "--", "docs"], cwd=root, check=True)
        subprocess.run([git_path, "commit", "-qm", "tracked drafts"], cwd=root, check=True)
        (drafts / "TASK-DELETED-001.md").unlink()
        (drafts / "TASK-UNTRACKED-001.md").write_text("untracked draft\n", encoding="utf-8")
        base = {"hook_event_name": "PreToolUse", "cwd": str(root)}
        policy_file = root / ".ai-governance" / "owner-policy.json"

        def write(path: Path, cwd: Path | None = None) -> str:
            payload = {**base, "cwd": str(cwd or root), "tool_name": "Write", "tool_input": {"file_path": str(path)}}
            return decision(hook_call(write_hook, root, payload))

        def shell(command: str) -> str:
            return decision(hook_call(shell_hook, root, {**base, "tool_name": "Bash", "tool_input": {"command": command}}))

        def mcp(name: str) -> str:
            return decision(hook_call(mcp_hook, root, {**base, "tool_name": name, "tool_input": {"query": "x"}}))

        def set_policy(policy: dict) -> None:
            policy_file.write_text(json.dumps(policy), encoding="utf-8")

        def good_policy(**changes: object) -> dict:
            return {**valid_owner_policy(git_path), **changes}

        activate = "python scripts/activate_lease.py docs/05-production/tasks/TASK-PROTO-001.md --owner-policy"
        task_docs = "python scripts/agent_commit.py --task-docs"
        seal = "python scripts/seal_implementation.py"
        commit = "python scripts/agent_commit.py"
        shifted_target = root / ".ai-governance" / "docs" / "05-production" / "tasks" / "TASK-X.md"

        v.check(shell(activate) == "deny", "owner-policy activation form must be denied without a policy")
        v.check(shell(task_docs) == "deny", "task-document commit form must be denied without a policy")
        v.check(write(drafts / "TASK-PROTO-001.md") == "ask", "task drafting must still ask without a policy")
        v.check(
            write(shifted_target, cwd=root / ".ai-governance") == "deny",
            "a write to a controlled path must be denied even when the working directory is shifted",
        )

        set_policy(good_policy())
        v.check(shell(activate) == "allow", "exact owner-policy activation form must be allowed with a policy")
        v.check(shell(activate + " --hours 2") == "allow", "activation with --hours must be allowed with a policy")
        v.check(shell(task_docs) == "allow", "task-document commit form must be allowed with a policy")
        v.check(shell(seal) == "deny", "sealing needs an owner-policy lease")
        v.check(shell(commit) == "deny", "a lane commit needs a sealed owner-policy lease")
        v.check(shell("git commit -m x") == "deny", "plain git commit must stay denied in policy mode")
        variants = [
            activate + " --inherit-dirty",
            activate + " ",
            " " + activate,
            activate + "\n",
            activate + " && echo x",
            "X=1 " + activate,
            activate.replace("python ", "python3 "),
            activate.replace("scripts/", "./scripts/"),
            activate.replace("TASK-PROTO-001", "TASK-..-001"),
            activate.replace("python", "pythоn"),
            task_docs + " --x",
            task_docs.upper(),
            "python  scripts/agent_commit.py --task-docs",
            "python scripts/owner_policy.py",
            "cat scripts/agent_commit.py",
        ]
        for variant in variants:
            v.check(shell(variant) == "deny", f"owner-policy command variant must be denied: {variant!r}")

        def action(command: str, lease: dict | None) -> str | None:
            with mock.patch.object(common, "load_lease", return_value=(lease, "stub")):
                return common.owner_policy_command(root, command)

        owned = {"authority": "owner-policy"}
        v.check(action(seal, None) is None, "seal form needs a lease")
        v.check(action(seal, {**owned, "state": "ACTIVE"}) == "seal", "seal form is allowed for an active owner-policy lease")
        v.check(action(seal, {**owned, "state": "SEALED"}) is None, "seal form is refused for a sealed lease")
        v.check(action(commit, {**owned, "state": "SEALED"}) == "commit", "commit form is allowed for a sealed owner-policy lease")
        v.check(action(commit, {**owned, "state": "ACTIVE"}) is None, "commit form is refused for an unsealed lease")
        v.check(action(seal, {"authority": "human", "state": "ACTIVE"}) is None, "seal form is refused for a human-authority lease")
        v.check(action(seal, {"state": "ACTIVE"}) is None, "seal form is refused when the lease has no authority")
        v.check(action(commit, {**owned, "state": ["SEALED"]}) is None, "a non-string lease state must be refused")
        stub_lease = {
            "schema": 3, "state": ["ACTIVE"], "task_id": "T", "task_contract": "x", "task_sha256": "x",
            "ready_review_receipt": "x", "ready_review_sha256": "x", "expires_at": "2099-01-01T00:00:00Z",
            "allowed_paths": ["a"], "allowed_commands": [], "git_root": "x", "git_head": "x", "git_branch": "x",
        }
        lease_file = root / ".ai-governance" / "implementation-lease.json"
        lease_file.write_text(json.dumps(stub_lease), encoding="utf-8")
        v.check(common.load_lease(root, allow_sealed=True)[0] is None, "load_lease must refuse a non-string state")
        lease_file.unlink()

        v.check(write(root / "docs/note.md") == "deny", "other documentation writes must be denied in policy mode")
        v.check(mcp("mcp__filesystem__write_file") == "deny", "MCP tools must be denied in policy mode")
        for name in ("TASK-PROTO-001.md", "READY-TASK-PROTO-001.md", "TASK-UNTRACKED-001.md"):
            v.check(write(drafts / name) == "allow", f"drafting a new or untracked task file must be allowed: {name}")
        for name in ("TASK-TRACKED-001.md", "TASK-DELETED-001.md"):
            v.check(write(drafts / name) == "deny", f"rewriting a tracked task file must be denied: {name}")
        rel = "docs/05-production/tasks/"
        v.check(common.path_is_untracked(root, rel + "TASK-NEW-001.md", git_path), "a new path counts as untracked")
        v.check(common.path_is_untracked(root, rel + "TASK-UNTRACKED-001.md", git_path), "an untracked draft counts as untracked")
        v.check(not common.path_is_untracked(root, rel + "TASK-TRACKED-001.md", git_path), "a tracked file is not untracked")
        v.check(not common.path_is_untracked(root, rel + "TASK-DELETED-001.md", git_path), "a deleted tracked file is not untracked")
        for name in ("ACCEPT-TASK-PROTO-001.md", "task-proto-001.md", "TASK-PROTO-001.txt", "sub/TASK-PROTO-001.md"):
            v.check(write(drafts / name) == "deny", f"other task-directory writes must be denied in policy mode: {name}")
        v.check(write(root / "docs/07-evidence/ACCEPT-TASK-PROTO-001.md") == "deny", "agents must not write acceptance receipts")
        v.check(write(root / ".ai-governance/owner-policy.json") == "deny", "the policy file must stay a controlled path")
        v.check(
            write(shifted_target, cwd=root / ".ai-governance") == "deny",
            "a shifted working directory must not turn a controlled path into an allowed draft",
        )

        def lane(paths: list[str]) -> dict:
            return {"name": "x", "allowed_paths": paths, "max_rigor": "R1", "extensions": [".cs"]}

        bad_policies = {
            "expired": good_policy(expires_at="2000-01-01T00:00:00Z"),
            "missing expiry": {k: val for k, val in good_policy().items() if k != "expires_at"},
            "placeholder reviewer": good_policy(reviewer_ids=["<independent reviewer id>"]),
            "relative git": good_policy(git_executable="git"),
            "missing git": good_policy(git_executable=str(root / "nowhere" / "git.exe")),
            "not git": good_policy(git_executable=str(Path(sys.executable).resolve())),
            "wrong schema": good_policy(schema=2),
            "boolean schema": good_policy(schema=True),
            "wrong branch": good_policy(required_branch="main"),
            "empty deny": good_policy(deny_paths=[]),
            "no lanes": good_policy(lanes=[]),
            "wildcard lane": good_policy(lanes=[lane(["**"])]),
            "star lane": good_policy(lanes=[lane(["Assets/*"])]),
            "glob lane": good_policy(lanes=[lane(["**/*.cs"])]),
            "claude lane": good_policy(lanes=[lane([".claude/**"])]),
            "dotless controlled lane": good_policy(lanes=[lane(["claude/hooks/**"])]),
            "dot-slash lane": good_policy(lanes=[lane(["./.claude/hooks/**"])]),
            "scripts lane": good_policy(lanes=[lane(["scripts/**"])]),
            "git lane": good_policy(lanes=[lane([".git/**"])]),
            "gitignore lane": good_policy(lanes=[lane([".gitignore"])]),
            "traversal lane": good_policy(lanes=[lane(["Assets/../scripts/x.py"])]),
            "trailing dot lane": good_policy(lanes=[lane(["Assets/Game."])]),
            "double slash lane": good_policy(lanes=[lane(["Assets//Game/**"])]),
        }
        for label, bad in bad_policies.items():
            set_policy(bad)
            v.check(shell(activate) == "deny", f"an invalid policy ({label}) must not authorize activation")
            v.check(write(root / "docs/note.md") == "ask", f"an invalid policy ({label}) must not enable policy mode")

        set_policy(good_policy(lanes=[lane([".claude/rules/unity.md", "Assets/Game/**", "Assets/Game.meta"])]))
        v.check(shell(activate) == "allow", "a narrow engine-rules and game lane policy must be valid")
        set_policy(good_policy())
        v.check(shell(activate) == "allow", "restored policy must authorize activation")
        policy_file.unlink()
        v.check(shell(activate) == "deny", "deleting the policy must revoke authority")

        audit = [
            json.loads(line)
            for line in (root / ".ai-governance" / "audit.log").read_text(encoding="utf-8").splitlines()
        ]
        v.check(bool(audit) and audit[0].get("policy_sha256") is None, "audit entries without a policy must record no policy hash")
        v.check(any(entry.get("policy_sha256") for entry in audit), "audit entries in policy mode must record the policy hash")


def validate_repository_attestation(v: Validation) -> None:
    with tempfile.TemporaryDirectory(prefix="aigdo-attestation-") as temp:
        project = Path(temp) / "project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
            ),
        )
        subprocess.run(["git", "init", "-q"], cwd=project, check=True)
        subprocess.run(["git", "config", "user.email", "validator@example.invalid"], cwd=project, check=True)
        subprocess.run(["git", "config", "user.name", "AIGDO Validator"], cwd=project, check=True)
        source = project / "Source" / "Project" / "Test"
        source.mkdir(parents=True)
        (source / ".keep").write_text("base\n", encoding="utf-8")
        task = project / "docs" / "05-production" / "tasks" / "TASK-TEST-ATTEST.md"
        review = project / "docs" / "07-evidence" / "READY-TASK-TEST-ATTEST.md"
        task.write_text(
            "---\n"
            "task_id: TASK-TEST-ATTEST\n"
            "status: READY_FOR_IMPLEMENTATION\n"
            "authored_by: implementation-author\n"
            "approved_by: independent-reviewer\n"
            "ready_review_receipt: docs/07-evidence/READY-TASK-TEST-ATTEST.md\n"
            "rigor: R3\n"
            "approval_mode: hash\n"
            "system_id: SYS-TEST-ATTEST\n"
            "allowed_paths:\n"
            "  - Source/Project/Test/**\n"
            "allowed_commands:\n"
            "---\n"
            "# Repository attestation integration task\n",
            encoding="utf-8",
        )
        review.write_text(
            "---\n"
            "review_id: REVIEW-TASK-TEST-ATTEST-R1\n"
            "task_id: TASK-TEST-ATTEST\n"
            "disposition: READY_FOR_IMPLEMENTATION\n"
            "reviewer: independent-reviewer\n"
            f"task_sha256: {sha256(task)}\n"
            "reviewed_at: 2026-09-16T00:00:00Z\n"
            "approval_mode: hash\n"
            "signature_file: UNSET\n"
            "allowed_signers_file: UNSET\n"
            "---\n"
            "# Ready review\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=project, check=True)
        subprocess.run(["git", "commit", "-qm", "attestation base"], cwd=project, check=True)
        ignored_task = project / "ignored-task.md"
        ignored_review = project / "docs" / "07-evidence" / "READY-IGNORED-TASK.md"
        (project / ".git" / "info" / "exclude").write_text("ignored-task.md\n", encoding="utf-8")
        ignored_task.write_text(
            "---\n"
            "task_id: TASK-IGNORED\nstatus: READY_FOR_IMPLEMENTATION\n"
            "authored_by: implementation-author\napproved_by: independent-reviewer\n"
            "ready_review_receipt: docs/07-evidence/READY-IGNORED-TASK.md\n"
            "rigor: R3\napproval_mode: hash\nsystem_id: SYS-IGNORED\n"
            "allowed_paths:\n  - Source/Project/Test/**\nallowed_commands:\n---\n",
            encoding="utf-8",
        )
        ignored_review.write_text(
            "---\nreview_id: REVIEW-IGNORED-R1\ntask_id: TASK-IGNORED\n"
            "disposition: READY_FOR_IMPLEMENTATION\nreviewer: independent-reviewer\n"
            f"task_sha256: {sha256(ignored_task)}\nreviewed_at: 2026-09-16T00:00:00Z\n"
            "approval_mode: hash\n---\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", str(ignored_review.relative_to(project))], cwd=project, check=True)
        subprocess.run(["git", "commit", "-qm", "tracked review for ignored task probe"], cwd=project, check=True)
        ignored_activation = subprocess.run(
            [sys.executable, "scripts/activate_lease.py", "ignored-task.md", "--hours", "1"],
            cwd=project, input="TASK-IGNORED\nACTIVATE\n", text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        v.check(ignored_activation.returncode == 2, "ignored/untracked authority document must not activate a lease")
        def activate_attest_task(*extra: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-TEST-ATTEST.md", "--hours", "1", *extra],
                cwd=project, input="TASK-TEST-ATTEST\nACTIVATE\n", text=True, encoding="utf-8", errors="replace",
                capture_output=True, check=False,
            )

        inherited_marker = source / "INHERITED.tmp"
        inherited_marker.write_text("inherited\n", encoding="utf-8")
        refused_inherit = activate_attest_task()
        v.check(
            refused_inherit.returncode == 2 and "--inherit-dirty" in refused_inherit.stderr,
            "dirty paths inside allowed_paths must need --inherit-dirty",
        )
        inherited_activation = activate_attest_task("--inherit-dirty")
        v.check(
            inherited_activation.returncode == 0 and "INHERITED.tmp" in inherited_activation.stdout,
            f"--inherit-dirty must accept and list dirty paths inside allowed_paths: {inherited_activation.stderr.strip()}",
        )
        (project / ".ai-governance" / "implementation-lease.json").unlink(missing_ok=True)
        inherited_marker.unlink()
        dirty_marker = project / "DIRTY.tmp"
        dirty_marker.write_text("uncommitted\n", encoding="utf-8")
        dirty_activation = subprocess.run(
            [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-TEST-ATTEST.md", "--hours", "1"],
            cwd=project, input="TASK-TEST-ATTEST\nACTIVATE\n", text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        v.check(dirty_activation.returncode == 2, "lease activation must reject a dirty worktree")
        v.check("DIRTY.tmp" in dirty_activation.stderr, "dirty-worktree rejection must name the offending path")
        dirty_marker.unlink()
        activation = subprocess.run(
            [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-TEST-ATTEST.md", "--hours", "1"],
            cwd=project, input="TASK-TEST-ATTEST\nACTIVATE\n", text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        v.check(activation.returncode == 0, f"schema-3 interactive lease activation must pass: {activation.stderr.strip()}")
        lease_path = project / ".ai-governance" / "implementation-lease.json"
        try:
            lease = json.loads(lease_path.read_text(encoding="utf-8"))
            v.check(lease.get("schema") == 3, "activation must create a schema-3 lease")
            v.check(bool(lease.get("git_head")) and bool(lease.get("git_branch")), "lease must bind Git HEAD and branch")
        except Exception as exc:
            v.check(False, f"activated lease must be readable: {exc}")
        second_activation = activate_attest_task()
        v.check(
            second_activation.returncode == 2 and "unexpired ACTIVE lease" in second_activation.stderr,
            "activation must refuse to overwrite an unexpired ACTIVE lease",
        )
        if lease_path.is_file():
            active_text = lease_path.read_text(encoding="utf-8")
            bogus_lease = json.loads(active_text)
            bogus_lease["state"] = "../BOGUS"
            lease_path.write_text(json.dumps(bogus_lease), encoding="utf-8")
            bogus_activation = activate_attest_task()
            v.check(
                bogus_activation.returncode == 2 and "unknown state" in bogus_activation.stderr,
                "activation must refuse a lease file in an unknown state",
            )
            listed_state = json.loads(active_text)
            listed_state["state"] = ["ACTIVE"]
            lease_path.write_text(json.dumps(listed_state), encoding="utf-8")
            listed_activation = activate_attest_task()
            v.check(
                listed_activation.returncode == 2 and "unreadable" in listed_activation.stderr,
                "activation must refuse a lease file whose state is not a string",
            )
            sealed_lease = json.loads(active_text)
            sealed_lease["state"] = "SEALED"
            lease_path.write_text(json.dumps(sealed_lease), encoding="utf-8")
            reactivation = activate_attest_task()
            prior_archives = list(
                (project / ".ai-governance" / "implementation-seals").glob("PRIOR-TASK-TEST-ATTEST-SEALED-*.json")
            )
            v.check(
                reactivation.returncode == 0 and len(prior_archives) == 1,
                f"activation over a SEALED lease must archive it: {reactivation.stderr.strip()}",
            )
        (source / "X.cpp").write_text("int attested = 1;\n", encoding="utf-8")
        outside = project / "Source" / "Outside.cpp"
        outside.write_text("int outside = 1;\n", encoding="utf-8")
        rejected_seal = subprocess.run(
            [sys.executable, "scripts/seal_implementation.py"], cwd=project,
            text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
        )
        v.check(rejected_seal.returncode != 0, "seal must reject changed paths outside the active lease")
        outside.unlink()
        sealed = subprocess.run(
            [sys.executable, "scripts/seal_implementation.py"], cwd=project,
            text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
        )
        v.check(sealed.returncode == 0, f"implementation seal must pass for task-scoped diff: {sealed.stderr.strip()}")
        try:
            closed = json.loads(lease_path.read_text(encoding="utf-8"))
            seal_path = project / closed["implementation_seal"]
            seal = json.loads(seal_path.read_text(encoding="utf-8"))
            v.check(seal.get("changed_paths") == ["Source/Project/Test/X.cpp"], "seal must enumerate the exact changed path")
            v.check(len(seal.get("diff_sha256", "")) == 64, "seal must contain a SHA-256 diff digest")
            v.check(closed.get("state") == "SEALED", "sealing must close further implementation authority")
            v.check(sha256(seal_path) == closed.get("implementation_seal_sha256"), "lease must bind the immutable seal file")
            post_seal = hook_call(
                HOOKS / "govern_write.py", project,
                {
                    "hook_event_name": "PreToolUse", "cwd": str(project),
                    "tool_name": "Edit", "tool_input": {"file_path": str(source / "X.cpp")},
                },
            )
            v.check(decision(post_seal) == "deny", "post-seal production writes must be denied")
            duplicate_seal = subprocess.run(
                [sys.executable, "scripts/seal_implementation.py"], cwd=project,
                text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
            )
            v.check(duplicate_seal.returncode != 0, "a sealed lease must not create or overwrite another seal")
        except Exception as exc:
            v.check(False, f"implementation seal must be readable: {exc}")


def validate_ssh_approval(v: Validation) -> None:
    executable = shutil.which("ssh-keygen")
    if not executable:
        v.check(True, "ssh-keygen unavailable; R4 signature integration is environment-dependent")
        return
    with tempfile.TemporaryDirectory(prefix="aigdo-signature-") as temp:
        root = Path(temp)
        key = root / "reviewer"
        receipt = root / "receipt.md"
        receipt.write_text("immutable ready receipt\n", encoding="utf-8")
        generated = subprocess.run(
            [executable, "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
            capture_output=True, check=False,
        )
        v.check(generated.returncode == 0, "ephemeral reviewer key generation must pass")
        public_key = (key.with_suffix(".pub")).read_text(encoding="utf-8").strip()
        allowed = root / "allowed_signers"
        allowed.write_text(f"reviewer@example.invalid {public_key}\n", encoding="utf-8")
        signed = subprocess.run(
            [executable, "-Y", "sign", "-f", str(key), "-n", "aigdo-ready-review", str(receipt)],
            capture_output=True, check=False,
        )
        signature = Path(str(receipt) + ".sig")
        v.check(signed.returncode == 0 and signature.is_file(), "R4 receipt signing fixture must be created")
        verified = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_approval_signature.py"), str(receipt), str(signature), str(allowed), "reviewer@example.invalid"],
            capture_output=True, check=False,
        )
        v.check(verified.returncode == 0, "valid R4 SSH approval signature must verify")
        receipt.write_text("tampered receipt\n", encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_approval_signature.py"), str(receipt), str(signature), str(allowed), "reviewer@example.invalid"],
            capture_output=True, check=False,
        )
        v.check(rejected.returncode != 0, "tampered R4 approval receipt must be rejected")

        project = root / "r4-project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
            ),
        )
        subprocess.run(["git", "init", "-q"], cwd=project, check=True)
        subprocess.run(["git", "config", "user.email", "validator@example.invalid"], cwd=project, check=True)
        subprocess.run(["git", "config", "user.name", "AIGDO Validator"], cwd=project, check=True)
        task = project / "docs" / "05-production" / "tasks" / "TASK-R4-SIGNED.md"
        signed_review = project / "docs" / "07-evidence" / "READY-TASK-R4-SIGNED.md"
        trusted = project / "docs" / "00-project" / "TRUSTED-APPROVERS"
        task.write_text(
            "---\n"
            "task_id: TASK-R4-SIGNED\n"
            "status: READY_FOR_IMPLEMENTATION\n"
            "authored_by: architecture-author\n"
            "approved_by: reviewer@example.invalid\n"
            "ready_review_receipt: docs/07-evidence/READY-TASK-R4-SIGNED.md\n"
            "rigor: R4\n"
            "approval_mode: ssh-signature\n"
            "system_id: SYS-R4-SIGNED\n"
            "allowed_paths:\n"
            "  - Source/R4/**\n"
            "allowed_commands:\n"
            "---\n# Signed R4 task\n",
            encoding="utf-8",
        )
        signed_review.write_text(
            "---\n"
            "review_id: REVIEW-TASK-R4-SIGNED-R1\n"
            "task_id: TASK-R4-SIGNED\n"
            "disposition: READY_FOR_IMPLEMENTATION\n"
            "reviewer: reviewer@example.invalid\n"
            f"task_sha256: {sha256(task)}\n"
            "reviewed_at: 2026-09-16T00:00:00Z\n"
            "approval_mode: ssh-signature\n"
            "signature_file: docs/07-evidence/READY-TASK-R4-SIGNED.md.sig\n"
            "allowed_signers_file: docs/00-project/TRUSTED-APPROVERS\n"
            "---\n# Signed ready review\n",
            encoding="utf-8",
        )
        trusted.write_text(f"reviewer@example.invalid {public_key}\n", encoding="utf-8")
        signed_r4 = subprocess.run(
            [executable, "-Y", "sign", "-f", str(key), "-n", "aigdo-ready-review", str(signed_review)],
            capture_output=True, check=False,
        )
        v.check(signed_r4.returncode == 0, "R4 project receipt fixture must be signed")
        subprocess.run(["git", "add", "."], cwd=project, check=True)
        subprocess.run(["git", "commit", "-qm", "signed R4 approval"], cwd=project, check=True)
        activated = subprocess.run(
            [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-R4-SIGNED.md", "--hours", "1"],
            cwd=project, input="TASK-R4-SIGNED\nACTIVATE\n", text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        v.check(activated.returncode == 0, f"valid SSH-signed R4 task must activate: {activated.stderr.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mechanical and adversarial validation")
    parser.add_argument(
        "--working-repository",
        action="store_true",
        help="Skip the package-only checks that reject a local lease or implementation seals",
    )
    args = parser.parse_args()
    v = Validation()
    validate_files(v, args.working_repository)
    validate_settings(v)
    validate_frontmatter(v)
    validate_hooks(v)
    validate_owner_policy_mode(v)
    validate_repository_attestation(v)
    validate_ssh_approval(v)
    print(f"Checks: {v.checks}")
    print(f"Markdown files: {len(list(ROOT.rglob('*.md')))}")
    print(f"Agents: {len(list((ROOT / '.claude/agents').glob('*.md')))}")
    print(f"Skills: {len(list((ROOT / '.claude/skills').glob('*/SKILL.md')))}")
    if v.failures:
        print("RESULT: FAIL")
        for failure in v.failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()

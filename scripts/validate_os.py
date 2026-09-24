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


def validate_policy_lib(v: Validation) -> None:
    import common
    import policy_lib

    git_path = shutil.which("git")
    if not git_path:
        v.check(False, "git must be available for the policy library tests")
        return
    policy = valid_owner_policy(str(Path(git_path).resolve()))
    policy["lanes"] = [
        {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**", "Assets/_Prototype.meta"], "max_rigor": "R1", "extensions": [".cs", ".meta", ".txt"]},
        {"name": "game", "allowed_paths": ["Assets/Game/**"], "max_rigor": "R2", "extensions": [".cs", ".meta"]},
    ]
    policy["policy_sha256"] = "0" * 64
    good_cs = "using System;\nusing System.Collections.Generic;\nusing UnityEngine;\nusing UnityEngine.UI;\n\npublic class A : MonoBehaviour { }\n"
    v.check(policy_lib.cs_scan(good_cs) == [], "an ordinary C# file must pass the scan")
    v.check(policy_lib.cs_scan("// note\n/// <summary>Doc.</summary>\nclass A { }\n") == [], "whole-line comments must pass the scan")
    bad_cs = {
        "using System.IO;": "namespace",
        "using System.Diagnostics;": "namespace",
        "using UnityEngine.Networking;": "namespace",
        "using static System.Math;": "using form",
        "using Alias = System.Text.StringBuilder;": "using form",
        "global using System;": "using form",
        "\ufeffusing Microsoft.Win32;\nclass A {}": "bom and namespace root",
        "namespace N { using System.Diagnostics; class A {} }": "using inside a namespace",
        "using System; using System.Net;": "second using on a line",
        "using /* c */ System.IO;": "comment inside a using",
        "class A { void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "comment splits a token",
        "class A { void F() { System // c\n .IO.File.Delete(\"x\"); } }": "line comment splits a token",
        "class A { string s = \"http://x\"; void F() { System.IO.File.Delete(s); } }": "slashes in a string hide nothing",
        "class A { string s = \"\\U00000053\"; }": "long unicode escape",
        "class A { void F() { Microsoft.Win32.Registry.CurrentUser.Close(); } }": "qualified registry access",
        "class A { void F() { System.AppDomain.CurrentDomain.Load(null); } }": "runtime loading",
        "class A { dynamic d; }": "dynamic",
        "class A { void F() { global::System.IO.File.Delete(\"x\"); } }": "global qualified name",
        "using UnityEditor;": "editor",
        "class A { [InitializeOnLoad] static A() {} }": "initialize on load",
        "class A { [DllImport(\"x\")] static extern void F(); }": "dll import",
        "class A { void F() { System.Diagnostics.Process.Start(\"x\"); } }": "process",
        "class A { void F() { var t = obj.GetType().GetMethod(\"M\"); } }": "reflection",
        "class A { string s = \"\\u0053\"; }": "unicode escape",
        "#if UNITY_EDITOR\nclass A {}\n#endif": "conditional compilation",
        "#define X\nclass A {}": "preprocessor define",
        "class A { string s = \"/*\"; void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "string with a comment opener",
        "class A { string s = \"//\"; void F() { System // c\n .IO.File.Delete(\"x\"); } }": "string with slashes and a line-comment split",
        "class A { string s = @\"/*\"; void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "verbatim string with a comment opener",
        "class A { void F() { Sys​tem.IO.File.Delete(\"x\"); } }": "invisible formatting character",
        "class A { void F() {\nSystem\n// c\n.IO.File.Delete(\"x\");\n} }": "whole-line comment splits a token",
        "class A { int x; // trailing\n}": "trailing comments are refused",
        "class A { string s = $\"{\"//\"}\"; void F() { System/*c*/.IO.File.Delete(s); } }": "interpolation hole with slashes",
        "#region x'\nclass A { void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "apostrophe in a directive",
        ("class A { void F() { Sys" + chr(0x200B) + "tem.IO.File.Delete(\"x\"); } }"): "invisible character built with chr",
        "class A { void F() {\nSystem\n#pragma warning disable\n.IO.File.Delete(\"x\");\n} }": "preprocessor directive splits a token",
        "#nullable enable\nclass A {}\n": "any preprocessor directive is refused",
        "//a\rSystem\r//b\r.IO.File.Delete(x);": "bare carriage returns hide a token behind comments",
        ("//a" + chr(0x2028) + "System" + chr(0x2028) + "//b" + chr(0x2028) + ".IO.File.Delete(x);"): "line separator hides a token behind comments",
        "class A { void F() { Unity.Foo.Bar(); } }": "unity qualified name",
        "class A { void F() { var m = typeof(A).Module; } }": "module",
        "class A { void F() { new WWW(\"x\"); } }": "www",
        "class A { void F() { PlayerPrefs.SetString(\"a\", \"b\"); } }": "player prefs",
        "class A { void F() { Application.OpenURL(\"x\"); } }": "open url",
    }
    for source, label in bad_cs.items():
        v.check(bool(policy_lib.cs_scan(source)), f"the C# scan must reject ({label}): {source[:40]!r}")
    v.check(policy_lib.cs_scan("class A { void F() { int x = Application.targetFrameRate; var y = obj.GetType(); var z = System.Math.Abs(1); } }") == [], "ordinary Application, GetType and System.Math use must pass")
    for text in (
        "-----BEGIN RSA PRIVATE KEY-----",
        "key = AKIAABCDEFGHIJKLMNOP",
        "ghp_" + "a" * 36,
        "https://user:pass@example.com/x",
        "password = hunter2hunter2",
    ):
        v.check(bool(policy_lib.secret_content_problems(text)), f"the secret scan must flag: {text[:30]!r}")
    v.check(policy_lib.secret_content_problems("public int Score = 10; // token count") == [], "harmless text must pass the secret scan")
    v.check(bool(policy_lib.LONG_RUN.search("A" * 130)), "a long base64-looking run must be flagged")
    v.check(policy_lib.LONG_RUN.search("public int Score = 10;") is None, "ordinary text must not look like an encoded run")
    for relative in (".env", "Assets/Game/id_rsa", "Assets/Game/server.pem", "Assets/Game/my_secret.json", "Assets/credentials.txt"):
        v.check(policy_lib.secret_path_problem(relative) is not None, f"secret-looking path must be flagged: {relative}")
    v.check(policy_lib.secret_path_problem("Assets/Game/Player.cs") is None, "an ordinary path must not be flagged")
    lane = policy["lanes"][0]
    v.check(policy_lib.path_problems(policy, lane, "Assets/_Prototype/A.cs") == [], "an in-lane path must pass")
    for relative, reason in (
        ("Assets/_Prototype/Editor/A.cs", "editor"),
        ("Assets/_Prototype/A.dll", "dll"),
        ("Assets/_Prototype/A.asmdef", "asmdef"),
        ("Assets/_Prototype/.gitignore", "gitignore"),
        ("Assets/_Prototype/A.png", "extension"),
        ("Assets/Game/A.cs", "other lane"),
        ("Assets/_Prototype/A.cs:stream", "stream"),
        ("Assets/_Prototype/A.cs.", "trailing dot"),
        (".claude/hooks/x.py", "controlled"),
        ("scripts/x.py", "policy deny"),
    ):
        v.check(bool(policy_lib.path_problems(policy, lane, relative)), f"a path must be refused ({reason}): {relative}")
    lease = {"lane": "prototype"}
    v.check(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"content": good_cs}) == [], "a compliant write must pass the write-time rules")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/Editor/A.cs", {"content": "class A {}"})), "a write into an Editor folder must be refused at write time")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"content": "using UnityEditor;"})), "a write with editor code must be refused at write time")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/n.txt", {"content": "AKIAABCDEFGHIJKLMNOP"})), "a write with a secret must be refused at write time")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"new_string": "System.IO.File.Delete(x);"})), "an edit fragment must be scanned at write time")
    v.check(bool(policy_lib.write_problems(policy, {"lane": "unknown"}, "Assets/_Prototype/A.cs", {})), "an unknown lease lane must refuse writes")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"content": "/*" * 150000})), "an oversized write must be refused before any scan")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"edits": [{"old_string": "a", "new_string": "System.IO.File.Delete(x);"}]})), "MultiEdit fragments must be scanned")
    with tempfile.TemporaryDirectory(prefix="aigdo-edit-") as scratch:
        scratch_root = Path(scratch)
        (scratch_root / "Assets" / "_Prototype").mkdir(parents=True)
        (scratch_root / "Assets" / "_Prototype" / "S.cs").write_text("class A { void F() { System } }", encoding="utf-8")
        split_edit = {"old_string": " } }", "new_string": ".IO.File.Delete(x); } }"}
        v.check(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", split_edit) == [], "a fragment alone can look harmless")
        v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/S.cs", split_edit, scratch_root)), "an edit must be judged on the resulting file")
        (scratch_root / "Assets" / "_Prototype" / "Huge.cs").write_text("x" * 900000, encoding="utf-8")
        v.check(
            bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/Huge.cs", {"old_string": "x", "new_string": "y"}, scratch_root)),
            "an edit to a file too large to check must be refused",
        )
    import time as _time

    started = _time.monotonic()
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/n.txt", {"content": "eyJ" * 60000})), "a long repeated token run must be refused without hanging")
    v.check(isinstance(policy_lib.write_problems(policy, lease, "Assets/_Prototype/n.txt", {"content": "://a:" * 39999}), list), "a long repeated credential-like run must finish")
    v.check(_time.monotonic() - started < 20, "the two long adversarial runs must finish within 20 seconds")
    v.check(len(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"edits": [{"old_string": "a", "new_string": "b"}] * 51})) > 0, "too many edits in one write must be refused")
    for entry, expected in (
        ("Assets/_Prototype/**", "prototype"),
        ("Assets/_Prototype/Sub/**", "prototype"),
        ("Assets/_Prototype/A.cs", "prototype"),
        ("Assets/_Prototype.meta", "prototype"),
        ("Assets/Game/**", "game"),
        ("Assets/Other/**", None),
        ("Assets/**", None),
        ("Assets/_PrototypeX/**", None),
    ):
        found = policy_lib.entry_lane(policy, entry)
        v.check((found["name"] if found else None) == expected, f"entry lane for {entry} must be {expected}")
    base = {"approval_mode": "hash", "approved_by": "independent-reviewer", "authored_by": "implementation-author",
            "rigor": "R1", "allowed_commands": [], "commit_subject": "Add prototype file", "allowed_paths": ["Assets/_Prototype/**"]}
    repo = {"git_branch": "agent/work"}
    no_root = Path(tempfile.gettempdir()) / "aigdo-no-such-root"

    def check(**changes: object) -> list[str]:
        problems, _ = policy_lib.policy_activation_check(no_root, policy, {**base, **changes}, {}, repo)
        return problems

    v.check(check() == [], "a compliant task must pass the activation checks")
    for label, changes in {
        "rigor above lane": {"rigor": "R2"},
        "rigor missing": {"rigor": "R9"},
        "commands": {"allowed_commands": ["dotnet build"]},
        "subject attribution": {"commit_subject": "Co-Authored-By: someone"},
        "subject charset": {"commit_subject": "bad $(x)"},
        "subject blank": {"commit_subject": "   "},
        "subject missing": {"commit_subject": None},
        "reviewer": {"approved_by": "somebody"},
        "self review": {"authored_by": "independent-reviewer"},
        "approval mode": {"approval_mode": "ssh-signature"},
        "outside lane": {"allowed_paths": ["Assets/Other/**"]},
        "two lanes": {"allowed_paths": ["Assets/_Prototype/**", "Assets/Game/**"]},
        "denied path": {"allowed_paths": ["Assets/_Prototype/Editor/**"]},
        "wildcard": {"allowed_paths": ["Assets/_Prototype/*.cs"]},
    }.items():
        v.check(bool(check(**changes)), f"the activation checks must refuse ({label})")
    v.check(policy_lib.policy_activation_check(no_root, policy, {**base, "rigor": "R2", "allowed_paths": ["Assets/Game/**"]}, {}, repo)[0] != [], "R2 must exceed the R1 policy cap")
    branch_repo = {"git_branch": "main"}
    v.check(bool(policy_lib.policy_activation_check(no_root, policy, base, {}, branch_repo)[0]), "the wrong branch must be refused")
    with tempfile.TemporaryDirectory(prefix="aigdo-branch-") as temp:
        root = Path(temp)
        (root / ".ai-governance").mkdir()
        target = root / ".ai-governance" / "owner-policy.json"
        main_policy = {
            **valid_owner_policy(str(Path(git_path).resolve())), "required_branch": "main",
            "commit_to_default_branch": True, "remote_name": "origin", "remote_url": "https://github.com/o/r",
            "max_unpushed_commits": 5,
        }
        target.write_text(json.dumps(main_policy), encoding="utf-8")
        v.check(common.load_owner_policy(root)[0] is not None, "a main-branch policy with every acknowledgement field must load")
        for label, changes in {
            "no acknowledgement": {"commit_to_default_branch": False},
            "no remote": {"remote_url": None},
            "credential url": {"remote_url": "https://user:pw@github.com/o/r"},
            "http url": {"remote_url": "http://github.com/o/r"},
            "traversal url": {"remote_url": "https://github.com/o/../r"},
            "other remote": {"remote_name": "upstream"},
            "no cap": {"max_unpushed_commits": 0},
            "other base": {"base_branch": "develop"},
            "rigor cap R3": {"required_branch": "agent/work", "effective_rigor_cap": "R3"},
            "lane rigor R4": {"required_branch": "agent/work", "lanes": [{"name": "x", "allowed_paths": ["Assets/X/**"], "max_rigor": "R4", "extensions": [".cs"]}]},
        }.items():
            target.write_text(json.dumps({**main_policy, **changes}), encoding="utf-8")
            v.check(common.load_owner_policy(root)[0] is None, f"a policy must be refused ({label})")
    v.check(common.matches_any(".git/config", common.CONTROLLED_PATHS), ".git internals must be controlled paths")
    v.check(not common.matches_any(".gitignore", common.CONTROLLED_PATHS), ".gitignore must not be a controlled path")


def validate_owner_policy_activation(v: Validation) -> None:
    git_path = shutil.which("git")
    if not git_path:
        v.check(False, "git must be available for the owner-policy activation tests")
        return
    git_path = str(Path(git_path).resolve())
    write_hook = HOOKS / "govern_write.py"
    with tempfile.TemporaryDirectory(prefix="aigdo-b1-") as temp:
        project = Path(temp) / "project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals",
                "scheduled_tasks.lock", "owner-policy.json", "lease-counter.json", "empty-hooks",
            ),
        )

        def git(*args: str) -> None:
            subprocess.run([git_path, *args], cwd=project, check=True, capture_output=True)

        git("init", "-q")
        git("symbolic-ref", "HEAD", "refs/heads/agent/work")
        git("config", "user.email", "validator@example.invalid")
        git("config", "user.name", "AIGDO Validator")
        task = project / "docs" / "05-production" / "tasks" / "TASK-POLICY-ATTEST.md"
        review = project / "docs" / "07-evidence" / "READY-TASK-POLICY-ATTEST.md"
        task.write_text(
            "---\n"
            "task_id: TASK-POLICY-ATTEST\n"
            "status: READY_FOR_IMPLEMENTATION\n"
            "authored_by: implementation-author\n"
            "approved_by: independent-reviewer\n"
            "ready_review_receipt: docs/07-evidence/READY-TASK-POLICY-ATTEST.md\n"
            "rigor: R1\n"
            "approval_mode: hash\n"
            "system_id: SYS-POLICY-ATTEST\n"
            "commit_subject: Add prototype test file\n"
            "allowed_paths:\n"
            "  - Assets/_Prototype/**\n"
            "allowed_commands:\n"
            "---\n"
            "# Owner-policy attestation task\n",
            encoding="utf-8",
        )
        review.write_text(
            "---\n"
            "review_id: REVIEW-TASK-POLICY-ATTEST-R1\n"
            "task_id: TASK-POLICY-ATTEST\n"
            "disposition: READY_FOR_IMPLEMENTATION\n"
            "reviewer: independent-reviewer\n"
            f"task_sha256: {sha256(task)}\n"
            "reviewed_at: 2026-09-16T00:00:00Z\n"
            "approval_mode: hash\n"
            "signature_file: UNSET\n"
            "allowed_signers_file: UNSET\n"
            "---\n# Ready review\n",
            encoding="utf-8",
        )
        plugins = project / "Assets" / "Plugins"
        plugins.mkdir(parents=True, exist_ok=True)
        (plugins / "P.cs").write_text("class P {}\n", encoding="utf-8")
        (plugins / "P.cs.meta").write_text("fileFormatVersion: 2\nguid: fedcba9876543210fedcba9876543210\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "policy base")
        policy_file = project / ".ai-governance" / "owner-policy.json"
        lease_path = project / ".ai-governance" / "implementation-lease.json"
        lane_dir = project / "Assets" / "_Prototype"

        def policy(**changes: object) -> dict:
            base = valid_owner_policy(git_path)
            base["lanes"] = [
                {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**"], "max_rigor": "R1", "extensions": [".cs", ".meta", ".txt", ".png", ".asset"]}
            ]
            return {**base, **changes}

        def write_policy(**changes: object) -> None:
            policy_file.write_text(json.dumps(policy(**changes)), encoding="utf-8")

        def activate(*extra: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-POLICY-ATTEST.md", "--owner-policy", *extra],
                cwd=project, input="", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
            )

        def seal() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "scripts/seal_implementation.py"],
                cwd=project, input="", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
            )

        def hook_write(relative: str, content: str | None = None) -> str:
            tool_input: dict = {"file_path": str(project / relative)}
            if content is not None:
                tool_input["content"] = content
            payload = {"hook_event_name": "PreToolUse", "cwd": str(project), "tool_name": "Write", "tool_input": tool_input}
            return decision(hook_call(write_hook, project, payload))

        v.check(activate().returncode == 2, "owner-policy activation must be refused without a policy file")
        write_policy()
        v.check(activate("--inherit-dirty").returncode == 2, "owner-policy activation must refuse --inherit-dirty")
        v.check(activate("--hours", "9").returncode == 2, "owner-policy activation must refuse hours above the policy limit")
        v.check(activate("--hours=9").returncode == 2, "owner-policy activation must refuse hours above the limit in the = form")
        v.check(activate("--hou", "2").returncode == 2, "an abbreviated --hours must be refused")
        for label, changes in {
            "reviewer": {"reviewer_ids": ["somebody-else"]},
            "lane": {"lanes": [{"name": "other", "allowed_paths": ["Assets/Other/**"], "max_rigor": "R1", "extensions": [".cs"]}]},
            "deny": {"deny_paths": ["Assets/_Prototype/**"]},
            "rigor cap": {"effective_rigor_cap": "R0", "lanes": [{"name": "prototype", "allowed_paths": ["Assets/_Prototype/**"], "max_rigor": "R0", "extensions": [".cs"]}]},
            "branch": {"required_branch": "agent/other"},
        }.items():
            write_policy(**changes)
            refused = activate()
            v.check(
                refused.returncode == 2 and not lease_path.exists(),
                f"owner-policy activation must be refused ({label}): {refused.stderr.strip()}",
            )
        write_policy(max_leases_per_day=2)
        first = activate()
        try:
            lease = json.loads(lease_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            lease = {}
        v.check(first.returncode == 0, f"a compliant task must activate under the policy without prompts: {first.stderr.strip()}")
        v.check(
            lease.get("authority") == "owner-policy" and lease.get("lane") == "prototype"
            and lease.get("commit_subject") == "Add prototype test file" and bool(lease.get("policy_sha256")),
            "an owner-policy lease must record its authority, lane, commit subject, and policy hash",
        )
        again = activate()
        v.check(again.returncode == 2 and "unexpired ACTIVE lease" in again.stderr, "a second activation while a lease is active must be refused")
        lease_path.unlink(missing_ok=True)
        v.check(activate().returncode == 0, "a second lease within the daily limit must activate")
        lease_path.unlink(missing_ok=True)
        limited = activate()
        v.check(limited.returncode == 2 and "daily lease limit" in limited.stderr, "the daily lease limit must be enforced")
        write_policy()
        v.check(activate().returncode == 0, "activation must succeed again once the limit allows it")

        lane_dir.mkdir(parents=True, exist_ok=True)
        (project / "Assets" / "Other").mkdir(parents=True, exist_ok=True)
        v.check(hook_write("Assets/_Prototype/Good.cs", "using UnityEngine;\nclass G {}\n") == "allow", "the write hook must allow a compliant lane write")
        v.check(hook_write("Assets/_Prototype/Editor/E.cs", "class E {}\n") == "deny", "the write hook must refuse an Editor-folder write")
        v.check(hook_write("Assets/_Prototype/Bad.cs", "using UnityEditor;\n") == "deny", "the write hook must refuse editor code")
        v.check(hook_write("Assets/_Prototype/note.txt", "AKIAABCDEFGHIJKLMNOP\n") == "deny", "the write hook must refuse a secret")
        v.check(hook_write("Assets/_Prototype/Cf.cs", "class C { void F() { Sys​tem.IO.File.Delete(\"x\"); } }\n") == "deny", "the write hook must refuse an invisible formatting character")
        v.check(hook_write("Assets/_Prototype/Big.cs", "/*" * 150000) == "deny", "the write hook must refuse an oversized write")
        v.check(hook_write("Assets/_Prototype/Cf2.cs", "class C { void F() { Sys" + chr(0x200B) + "tem.IO.File.Delete(\"x\"); } }\n") == "deny", "the write hook must refuse an invisible character built with chr")
        v.check(hook_write("Assets/_Prototype/Tr.cs", "class C { int x; // trailing\n}\n") == "deny", "the write hook must refuse a trailing comment")
        v.check(hook_write("Assets/_Prototype/evil.dll", "MZ") == "deny", "the write hook must refuse a forbidden extension")
        v.check(hook_write("Assets/Other/X.cs", "class X {}\n") == "deny", "the write hook must refuse a path outside the lease")
        policy_file.unlink()
        v.check(hook_write("Assets/_Prototype/Good.cs", "using UnityEngine;\nclass G {}\n") == "deny", "deleting the policy must stop an active owner-policy lease")
        gone = seal()
        v.check(gone.returncode != 0 and "Owner policy" in gone.stderr, "the seal must refuse when the policy is gone")
        write_policy()
        v.check(hook_write("Assets/_Prototype/Good.cs", "using UnityEngine;\nclass G {}\n") == "allow", "restoring the identical policy must restore the lease")

        (lane_dir / "keep.txt").write_text("ok\n", encoding="utf-8")
        (project / ".git" / "info" / "exclude").write_text("ignored.txt\n", encoding="utf-8")
        bad_files: dict[str, str | bytes] = {
            "Bad.cs": "using UnityEditor;\nclass A {}\n",
            "evil.dll": "MZ",
            ".gitignore": "x\n",
            "note.txt": "AKIAABCDEFGHIJKLMNOP\n",
            "ignored.txt": "hidden\n",
            "utf16.cs": "using System;\nclass A {}\n".encode("utf-16"),
            "bom.cs": "\ufeffusing Microsoft.Win32;\nclass B {}\n".encode("utf-8"),
            "pic.png": b"AKIAABCDEFGHIJKLMNOP",
            "split.cs": "class C { void F() { System /* c */ . IO . File . Delete(\"x\"); } }\n",
            "ref.asset": "m_Script: {fileID: 11500000, guid: fedcba9876543210fedcba9876543210, type: 3}\n",
            "quote.cs": "class Q { string s = \"/*\"; void F() { System /* c */ . IO . File . Delete(\"x\"); } }\n",
        }
        for name, content in bad_files.items():
            data = content if isinstance(content, bytes) else content.encode("utf-8")
            (lane_dir / name).write_bytes(data)
            refused = seal()
            v.check(refused.returncode != 0 and "owner-policy seal refused" in refused.stderr, f"the seal must refuse a lane file ({name}): {refused.stderr.strip()}")
            (lane_dir / name).unlink()
        (lane_dir / "A.cs.meta").write_text("fileFormatVersion: 2\nguid: 0123456789abcdef0123456789abcdef\n", encoding="utf-8")
        (lane_dir / "B.cs.meta").write_text("fileFormatVersion: 2\nguid: 0123456789abcdef0123456789abcdef\n", encoding="utf-8")
        duplicate = seal()
        v.check(duplicate.returncode != 0 and "duplicate .meta GUID" in duplicate.stderr, "the seal must refuse duplicate .meta GUIDs")
        (lane_dir / "B.cs.meta").unlink()
        (project / "Assets" / "Other" / "X.cs").write_text("class X {}\n", encoding="utf-8")
        outside = seal()
        v.check(outside.returncode != 0 and "outside lease" in outside.stderr, "the seal must refuse a path outside the lease")
        (project / "Assets" / "Other" / "X.cs").unlink()
        write_policy(max_total_bytes=1999999)
        changed = seal()
        v.check(changed.returncode != 0 and "changed since activation" in changed.stderr, "the seal must refuse a policy changed after activation")
        write_policy()
        (lane_dir / "A.cs").write_text("using UnityEngine;\npublic class A : MonoBehaviour { }\n", encoding="utf-8")
        sealed = seal()
        v.check(sealed.returncode == 0, f"a compliant lane change must seal: {sealed.stderr.strip()}")
        try:
            sealed_lease = json.loads(lease_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            sealed_lease = {}
        v.check(sealed_lease.get("state") == "SEALED" and sealed_lease.get("authority") == "owner-policy", "the sealed lease must keep its owner-policy authority")


def validate_repository_attestation(v: Validation) -> None:
    with tempfile.TemporaryDirectory(prefix="aigdo-attestation-") as temp:
        project = Path(temp) / "project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
                "owner-policy.json", "lease-counter.json", "empty-hooks",
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
                "owner-policy.json", "lease-counter.json", "empty-hooks",
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
    validate_policy_lib(v)
    validate_owner_policy_activation(v)
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

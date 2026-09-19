#!/usr/bin/env python3
"""PROPOSED Patch A (revision 3) for OWNER-POLICY-001: inert without an owner policy file. Human-run only.

Adds: strict policy loading and validation, exact owner-policy command recognition, `ask` -> `deny`
in policy mode, drafting writes for NEW or untracked task contracts and receipts in policy mode,
project-root-relative and case-insensitive path checks in the write hook, `allow_sealed` in
load_lease, the policy hash in the audit log, controlled-path and forbidden-name additions,
.gitignore entries, and tests that run in a real temporary Git repository.

Dry run by default: every old snippet must occur exactly once and the patched Python must compile.
Nothing is written without --apply, and --apply needs an interactive terminal. Only the five listed
target files can be edited. Verify this file's SHA-256 against the value in the delivery message
before running it (see PATCH-A.md). Revert with `git restore <files>`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

ALLOWED_TARGETS = frozenset(
    {
        ".claude/hooks/common.py",
        ".claude/hooks/govern_shell.py",
        ".claude/hooks/govern_write.py",
        "scripts/validate_os.py",
        ".gitignore",
    }
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str) -> None:
    EDITS.append((path, old, new))


# --- .claude/hooks/common.py -----------------------------------------------------------------
edit(
    ".claude/hooks/common.py",
    r'''import os
import subprocess
import sys
''',
    r'''import os
import re
import subprocess
import sys
''',
)
edit(
    ".claude/hooks/common.py",
    r'''    "scripts/artifact_digest.py",
''',
    r'''    "scripts/artifact_digest.py",
    "scripts/owner_policy.py",
    "scripts/agent_commit.py",
''',
)
edit(
    ".claude/hooks/common.py",
    r'''def git_dirty_paths(root: Path) -> tuple[list[str] | None, str]:''',
    r'''POLICY_FILE = ".ai-governance/owner-policy.json"
RIGOR_LEVELS = ("R0", "R1", "R2", "R3", "R4")
TASK_DOCUMENT_WRITE = re.compile(r"docs/05-production/tasks/(?:TASK|READY-TASK)-[A-Z0-9._-]+\.md")
OWNER_POLICY_COMMANDS = (
    (
        "activate",
        re.compile(
            r"python scripts/activate_lease\.py docs/05-production/tasks/(?!.*\.\.)[A-Z0-9][A-Z0-9._-]{2,80}\.md"
            r" --owner-policy( --hours [0-9]{1,2}(\.[0-9])?)?"
        ),
    ),
    ("seal", re.compile(r"python scripts/seal_implementation\.py")),
    ("commit", re.compile(r"python scripts/agent_commit\.py")),
    ("task-docs", re.compile(r"python scripts/agent_commit\.py --task-docs")),
)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def _is_str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def _normalize(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def _lane_path_problem(path: str) -> str | None:
    literal = path[:-3] if path.endswith("/**") else path
    segments = literal.split("/")
    if (
        not literal
        or any(char in literal for char in "*?[]\\:")
        or literal.startswith(("/", "~"))
        or any(part in {"", ".", ".."} or part.endswith((".", " ")) for part in segments)
        or any(part.lstrip(".").casefold().startswith("git") for part in segments)
    ):
        return f"Owner policy lane path is unsafe: {path}"
    folded = _normalize(literal).casefold().rstrip("/")
    for controlled in CONTROLLED_PATHS:
        prefix = _normalize(controlled).casefold().rstrip("*").rstrip("/")
        if prefix.startswith(folded) or folded.startswith(prefix):
            return f"Owner policy lane path overlaps controlled governance files: {path}"
    return None


def _policy_problem(policy: Any) -> str | None:
    if not isinstance(policy, dict) or type(policy.get("schema")) is not int or policy["schema"] != 1:
        return "Owner policy schema is invalid"
    if "expires_at" not in policy:
        return "Owner policy must state expires_at (null means indefinite)"
    if policy["expires_at"] is not None:
        try:
            expires = datetime.fromisoformat(str(policy["expires_at"]).replace("Z", "+00:00"))
        except ValueError:
            return "Owner policy expiry is invalid"
        if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
            return "Owner policy has expired"
    for key in ("policy_id", "required_branch", "base_branch"):
        if not isinstance(policy.get(key), str) or not policy[key]:
            return f"Owner policy field {key} is invalid"
    if not policy["required_branch"].startswith("agent/"):
        return "Owner policy required_branch must start with agent/"
    git_executable = policy.get("git_executable")
    if not isinstance(git_executable, str) or "<" in git_executable:
        return "Owner policy git_executable is invalid"
    git_path = Path(git_executable)
    if not git_path.is_absolute() or not git_path.is_file() or git_path.name.casefold() not in {"git", "git.exe"}:
        return "Owner policy git_executable must be an absolute path to an existing git executable"
    if policy.get("effective_rigor_cap") not in RIGOR_LEVELS:
        return "Owner policy effective_rigor_cap is invalid"
    hours = policy.get("max_lease_hours")
    if isinstance(hours, bool) or not isinstance(hours, (int, float)) or not 0 < hours <= 24:
        return "Owner policy max_lease_hours is invalid"
    for key in ("max_changed_paths", "max_total_bytes", "max_leases_per_day", "max_unmerged_commits", "max_unmerged_paths"):
        if not _is_int(policy.get(key)):
            return f"Owner policy field {key} is invalid"
    if not _is_str_list(policy.get("allowed_commands")):
        return "Owner policy field allowed_commands is invalid"
    if not _is_str_list(policy.get("deny_paths")) or not policy["deny_paths"]:
        return "Owner policy deny_paths must be a non-empty list"
    reviewers = policy.get("reviewer_ids")
    if not _is_str_list(reviewers) or not reviewers or any("<" in item for item in reviewers):
        return "Owner policy reviewer_ids must be a non-empty list without placeholders"
    lanes = policy.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        return "Owner policy has no lanes"
    for lane in lanes:
        if (
            not isinstance(lane, dict)
            or not isinstance(lane.get("name"), str)
            or not lane["name"]
            or not _is_str_list(lane.get("allowed_paths"))
            or not lane["allowed_paths"]
            or lane.get("max_rigor") not in RIGOR_LEVELS
            or not _is_str_list(lane.get("extensions"))
        ):
            return "Owner policy lane is invalid"
        for path in lane["allowed_paths"]:
            problem = _lane_path_problem(path)
            if problem:
                return problem
    return None


def load_owner_policy(root: Path) -> tuple[dict[str, Any] | None, str]:
    """Return the owner policy when the file exists and passes every structural check."""
    policy_path = root / POLICY_FILE
    if not policy_path.is_file():
        return None, "No owner policy"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, "Owner policy is unreadable"
    problem = _policy_problem(policy)
    if problem:
        return None, problem
    policy["policy_sha256"] = file_sha256(policy_path)
    return policy, "Owner policy is valid"


def owner_policy_command(root: Path, command: str) -> str | None:
    """Return the action name when the raw command is an exact owner-policy form the policy allows."""
    if not (command.isascii() and command.isprintable()):
        return None
    policy, _ = load_owner_policy(root)
    if policy is None:
        return None
    action = next((name for name, pattern in OWNER_POLICY_COMMANDS if pattern.fullmatch(command)), None)
    if action in {"activate", "task-docs"}:
        return action
    if action not in {"seal", "commit"}:
        return None
    lease, _ = load_lease(root, allow_sealed=True)
    if not lease or lease.get("authority") != "owner-policy":
        return None
    if (action == "seal" and lease["state"] == "ACTIVE") or (action == "commit" and lease["state"] == "SEALED"):
        return action
    return None


def path_is_untracked(root: Path, relative: str, git: str = "git") -> bool:
    """True when Git does not track the path (an existing untracked draft counts); false when tracked.

    If Git cannot answer, only a brand-new path counts as untracked (fail closed)."""
    try:
        result = subprocess.run(
            [git, "--literal-pathspecs", "ls-files", "--error-unmatch", "--", relative],
            cwd=root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return not (root / relative).exists()
    if result.returncode == 0:
        return False
    if result.returncode == 1:
        return True
    return not (root / relative).exists()


def git_dirty_paths(root: Path) -> tuple[list[str] | None, str]:''',
)
edit(
    ".claude/hooks/common.py",
    r'''    root = project_root()
    lease, _ = load_lease(root)
    audit_dir = root / ".ai-governance"''',
    r'''    root = project_root()
    policy, _ = load_owner_policy(root)
    if decision == "ask" and policy is not None:
        decision = "deny"
        reason = f"{reason} (owner-policy mode: no human is available to answer a prompt)"
    lease, _ = load_lease(root)
    audit_dir = root / ".ai-governance"''',
)
edit(
    ".claude/hooks/common.py",
    r'''        "task_id": lease.get("task_id") if lease else None,
    }''',
    r'''        "task_id": lease.get("task_id") if lease else None,
        "policy_sha256": policy["policy_sha256"] if policy else None,
    }''',
)
edit(
    ".claude/hooks/common.py",
    r'''def load_lease(root: Path) -> tuple[dict[str, Any] | None, str]:
    lease_path = root / ".ai-governance" / "implementation-lease.json"''',
    r'''def load_lease(root: Path, allow_sealed: bool = False) -> tuple[dict[str, Any] | None, str]:
    lease_path = root / ".ai-governance" / "implementation-lease.json"''',
)
edit(
    ".claude/hooks/common.py",
    r'''    if lease["schema"] != 3 or lease["state"] != "ACTIVE":
        return None, "Implementation lease is inactive"''',
    r'''    accepted_states = {"ACTIVE", "SEALED"} if allow_sealed else {"ACTIVE"}
    if lease["schema"] != 3 or not isinstance(lease["state"], str) or lease["state"] not in accepted_states:
        return None, "Implementation lease is inactive"''',
)

# --- .claude/hooks/govern_shell.py -------------------------------------------------------------
edit(
    ".claude/hooks/govern_shell.py",
    r'''from common import emit_decision, load_lease, project_root, read_hook_input, run_fail_closed''',
    r'''from common import emit_decision, load_lease, owner_policy_command, project_root, read_hook_input, run_fail_closed''',
)
edit(
    ".claude/hooks/govern_shell.py",
    r'''UNSAFE_GIT_OPTIONS = {"--output", "--ext-diff", "--textconv", "--exec-path"}
''',
    r'''UNSAFE_GIT_OPTIONS = {"--output", "--ext-diff", "--textconv", "--exec-path"}
LEASE_SCRIPTS = (
    "activate_lease.py", "deactivate_lease.py", "seal_implementation.py", "agent_commit.py", "owner_policy.py",
)
''',
)
edit(
    ".claude/hooks/govern_shell.py",
    r'''    if any(name in lowered for name in ("activate_lease.py", "deactivate_lease.py", "seal_implementation.py")):''',
    r'''    if any(name in lowered for name in LEASE_SCRIPTS):''',
)
edit(
    ".claude/hooks/govern_shell.py",
    r'''        if any(name in joined for name in ("activate_lease.py", "deactivate_lease.py", "seal_implementation.py")):''',
    r'''        if any(name in joined for name in LEASE_SCRIPTS):''',
)
edit(
    ".claude/hooks/govern_shell.py",
    r'''    normalized = command.strip()
    tokens = split_command(normalized)''',
    r'''    action = owner_policy_command(project_root(), command)
    if action:
        emit_decision(data, "allow", f"Exact owner-policy command form is authorized: {action}")
        return
    normalized = command.strip()
    tokens = split_command(normalized)''',
)

# --- .claude/hooks/govern_write.py -------------------------------------------------------------
edit(
    ".claude/hooks/govern_write.py",
    r'''from common import (
    ALWAYS_DOCUMENTATION_PATHS,
    CONTROLLED_PATHS,
    load_lease,''',
    r'''from common import (
    ALWAYS_DOCUMENTATION_PATHS,
    CONTROLLED_PATHS,
    TASK_DOCUMENT_WRITE,
    load_lease,
    load_owner_policy,
    path_is_untracked,''',
)
edit(
    ".claude/hooks/govern_write.py",
    r'''    lease, lease_reason = load_lease(project_root())
    if lease and matches_any(relative, lease["allowed_paths"]):
        emit_decision(data, "allow", f"Path is inside active task {lease['task_id']}: {relative}")
        return''',
    r'''    root_relative = relative_target(target, project_root())
    if root_relative is None:
        emit_decision(data, "deny", "Writes outside the project root are not allowed")
        return
    if matches_any(root_relative, CONTROLLED_PATHS) or matches_any(
        root_relative.casefold(), tuple(item.casefold() for item in CONTROLLED_PATHS)
    ):
        emit_decision(data, "deny", f"Governance-controlled path cannot be modified by an agent: {root_relative}")
        return

    lease, lease_reason = load_lease(project_root())
    if lease and matches_any(root_relative, lease["allowed_paths"]):
        emit_decision(data, "allow", f"Path is inside active task {lease['task_id']}: {root_relative}")
        return''',
)
edit(
    ".claude/hooks/govern_write.py",
    r'''    if matches_any(relative, ALWAYS_DOCUMENTATION_PATHS):''',
    r'''    policy = load_owner_policy(project_root())[0]
    if (
        policy is not None
        and TASK_DOCUMENT_WRITE.fullmatch(root_relative)
        and path_is_untracked(project_root(), root_relative, policy["git_executable"])
    ):
        emit_decision(data, "allow", f"Owner-policy mode allows drafting a task contract or receipt: {root_relative}")
        return

    if matches_any(root_relative, ALWAYS_DOCUMENTATION_PATHS):''',
)

# --- .gitignore --------------------------------------------------------------------------------
edit(
    ".gitignore",
    r'''.ai-governance/audit.log
''',
    r'''.ai-governance/audit.log
.ai-governance/owner-policy.json
.ai-governance/lease-counter.json
.ai-governance/empty-hooks/
''',
)

# --- scripts/validate_os.py: shifted-cwd lease test, owner-policy tests ------------------------------
edit(
    "scripts/validate_os.py",
    r'''        v.check(write(root / "Source/Other.cpp", "Edit") == "deny", "active lease must deny out-of-scope write")
''',
    r'''        v.check(write(root / "Source/Other.cpp", "Edit") == "deny", "active lease must deny out-of-scope write")
        shifted_cwd = {**base, "cwd": str(root / "Source"), "tool_name": "Edit"}
        v.check(
            decision(hook_call(write_hook, root, {**shifted_cwd, "tool_input": {"file_path": str(root / "Source/Game/X.cpp")}})) == "allow",
            "a lease write must be judged from the project root even when the working directory is shifted",
        )
        v.check(
            decision(hook_call(write_hook, root, {**shifted_cwd, "tool_input": {"file_path": str(root / "Source/Source/Game/Y.cpp")}})) == "deny",
            "a shifted working directory must not let an out-of-scope path pass as in-scope",
        )
''',
)
edit(
    "scripts/validate_os.py",
    r'''def validate_repository_attestation(v: Validation) -> None:''',
    r'''def valid_owner_policy(git_path: str) -> dict:
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


def validate_repository_attestation(v: Validation) -> None:''',
)
edit(
    "scripts/validate_os.py",
    r'''    validate_hooks(v)
    validate_repository_attestation(v)
''',
    r'''    validate_hooks(v)
    validate_owner_policy_mode(v)
    validate_repository_attestation(v)
''',
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the changes (default is a dry run)")
    args = parser.parse_args()

    if args.apply and not sys.stdin.isatty():
        print("Refusing --apply without an interactive terminal.")
        return 1

    contents: dict[str, str] = {}
    newlines: dict[str, str] = {}
    problems: list[str] = []
    for relative, old, new in EDITS:
        if relative not in ALLOWED_TARGETS:
            problems.append(f"{relative}: not an allowed target")
            continue
        path = ROOT / relative
        if relative not in contents:
            try:
                text = path.read_bytes().decode("utf-8")
            except OSError as exc:
                problems.append(f"{relative}: cannot read ({exc})")
                continue
            newlines[relative] = "\r\n" if "\r\n" in text else "\n"
            contents[relative] = text
        style = newlines[relative]
        old_n = old.replace("\n", style)
        new_n = new.replace("\n", style)
        count = contents[relative].count(old_n)
        if count != 1:
            problems.append(f"{relative}: expected exactly 1 match, found {count} for: {old.strip().splitlines()[0]}")
            continue
        contents[relative] = contents[relative].replace(old_n, new_n)

    if not problems:
        for relative, text in contents.items():
            if relative.endswith(".py"):
                try:
                    compile(text, relative, "exec")
                except SyntaxError as exc:
                    problems.append(f"{relative}: patched file would not compile ({exc})")

    if problems:
        print("NOT APPLIED. Fix these first (the repository may have changed since the proposal):")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    for relative in contents:
        print(f"{'WRITE' if args.apply else 'WOULD WRITE'}: {relative}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to write these files.")
        return 0
    for relative, text in contents.items():
        (ROOT / relative).write_bytes(text.encode("utf-8"))
    print("Applied. Now read `git diff` for these files and run the verification steps in PATCH-A.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

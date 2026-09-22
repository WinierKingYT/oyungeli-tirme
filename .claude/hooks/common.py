"""Shared deterministic governance helpers. Standard library only."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONTROLLED_PATHS = (
    ".ai-governance/**",
    ".claude/hooks/**",
    ".claude/settings.json",
    "scripts/activate_lease.py",
    "scripts/deactivate_lease.py",
    "scripts/seal_implementation.py",
    "scripts/verify_approval_signature.py",
    "scripts/doctor.py",
    "scripts/task_digest.py",
    "scripts/artifact_digest.py",
    "scripts/owner_policy.py",
    "scripts/agent_commit.py",
    "scripts/validate_os.py",
    "tests/governance_attack_corpus.json",
    ".github/workflows/aigdo-validation.yml",
)

ALWAYS_DOCUMENTATION_PATHS = (
    "docs/**",
    "README.md",
)


def read_hook_input() -> dict[str, Any]:
    try:
        return json.load(__import__("sys").stdin)
    except Exception:
        return {}


def response(decision: str, reason: str, context: str | None = None) -> None:
    payload: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    if context:
        payload["hookSpecificOutput"]["additionalContext"] = context
    print(json.dumps(payload, ensure_ascii=False))


def emit_decision(
    data: dict[str, Any], decision: str, reason: str, context: str | None = None
) -> None:
    """Audit and emit one schema-valid PreToolUse decision."""
    root = project_root()
    policy, _ = load_owner_policy(root)
    if decision == "ask" and policy is not None:
        decision = "deny"
        reason = f"{reason} (owner-policy mode: no human is available to answer a prompt)"
    lease, _ = load_lease(root)
    audit_dir = root / ".ai-governance"
    audit_dir.mkdir(parents=True, exist_ok=True)
    tool_input = data.get("tool_input", {})
    subject = (
        tool_input.get("file_path")
        or tool_input.get("notebook_path")
        or tool_input.get("command")
        or "<missing>"
    )
    event = {
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tool": data.get("tool_name", "<missing>"),
        "subject": str(subject)[:1000],
        "decision": decision,
        "reason": reason[:1000],
        "task_id": lease.get("task_id") if lease else None,
        "policy_sha256": policy["policy_sha256"] if policy else None,
    }
    with (audit_dir / "audit.log").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    response(decision, reason, context)


def run_fail_closed(main_function: Any) -> None:
    """A policy hook must block on internal failure; exit 1 is non-blocking."""
    try:
        if os.environ.get("AIGDO_TEST_FORCE_ERROR") == "1":
            raise RuntimeError("forced hook failure for validation")
        main_function()
    except BaseException as exc:  # hook boundary must also catch SystemExit
        print(
            f"AI Game Development OS policy hook failed closed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(2) from None


def project_root() -> Path:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(root).resolve()


def working_root(data: dict[str, Any]) -> Path:
    return Path(data.get("cwd") or project_root()).resolve()


def relative_target(target: str, cwd: Path) -> str | None:
    try:
        resolved = Path(target).expanduser().resolve(strict=False)
        return resolved.relative_to(cwd).as_posix()
    except (OSError, ValueError):
        return None


def matches_any(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(
        fnmatch.fnmatchcase(normalized, pattern.lstrip("./"))
        or fnmatch.fnmatchcase(normalized + "/", pattern.lstrip("./"))
        for pattern in patterns
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_state(root: Path) -> tuple[dict[str, str] | None, str]:
    """Return the repository identity used to bind implementation authority."""
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False, timeout=10,
        )
        if top.returncode != 0:
            return None, "Project is not inside a Git worktree"
        git_root = Path(top.stdout.strip()).resolve()
        if git_root != root.resolve():
            return None, "AI Game Development OS must be installed at the Git repository root"
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False, timeout=10,
        )
        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False, timeout=10,
        )
        if head.returncode != 0 or branch.returncode != 0:
            return None, "Git repository has no readable committed revision"
        return {
            "git_root": str(git_root),
            "git_head": head.stdout.strip(),
            "git_branch": branch.stdout.strip() or "DETACHED",
        }, "Git repository identity is valid"
    except (OSError, subprocess.SubprocessError):
        return None, "Git repository identity could not be verified"


def git_worktree_clean(root: Path) -> tuple[bool, str]:
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False, "Git worktree status could not be verified"
    if status.returncode != 0:
        return False, "Git worktree status could not be verified"
    if status.stdout:
        return False, "Git worktree must be clean before lease activation"
    return True, "Git worktree is clean"


POLICY_FILE = ".ai-governance/owner-policy.json"
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


def git_dirty_paths(root: Path) -> tuple[list[str] | None, str]:
    """Return every path that differs from HEAD, including untracked files."""
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None, "Git worktree status could not be verified"
    if status.returncode != 0:
        return None, "Git worktree status could not be verified"
    entries = status.stdout.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if ("R" in entry[:2] or "C" in entry[:2]) and index < len(entries):
            paths.append(entries[index])
            index += 1
    return paths, "Git worktree status read"


def load_lease(root: Path, allow_sealed: bool = False) -> tuple[dict[str, Any] | None, str]:
    lease_path = root / ".ai-governance" / "implementation-lease.json"
    if not lease_path.is_file():
        return None, "No active implementation lease"
    try:
        lease = json.loads(lease_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "Implementation lease is unreadable"

    required = {
        "schema",
        "state",
        "task_id",
        "task_contract",
        "task_sha256",
        "ready_review_receipt",
        "ready_review_sha256",
        "expires_at",
        "allowed_paths",
        "allowed_commands",
        "git_root",
        "git_head",
        "git_branch",
    }
    if not required.issubset(lease):
        return None, "Implementation lease is structurally invalid"
    accepted_states = {"ACTIVE", "SEALED"} if allow_sealed else {"ACTIVE"}
    if lease["schema"] != 3 or not isinstance(lease["state"], str) or lease["state"] not in accepted_states:
        return None, "Implementation lease is inactive"
    try:
        expires = datetime.fromisoformat(lease["expires_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None, "Implementation lease expiry is invalid"
    if expires <= datetime.now(timezone.utc):
        return None, "Implementation lease has expired"

    current_git, git_reason = git_state(root)
    if not current_git:
        return None, git_reason
    for field in ("git_root", "git_head", "git_branch"):
        if current_git[field] != lease[field]:
            return None, f"Repository {field} changed after lease activation"

    task_path = (root / lease["task_contract"]).resolve(strict=False)
    try:
        task_path.relative_to(root)
    except ValueError:
        return None, "Task contract is outside the project"
    if not task_path.is_file():
        return None, "Task contract no longer exists"
    if file_sha256(task_path) != lease["task_sha256"]:
        return None, "Task contract changed after lease activation"

    review_path = (root / lease["ready_review_receipt"]).resolve(strict=False)
    try:
        review_path.relative_to(root)
    except ValueError:
        return None, "Ready-review receipt is outside the project"
    if not review_path.is_file():
        return None, "Ready-review receipt no longer exists"
    if file_sha256(review_path) != lease["ready_review_sha256"]:
        return None, "Ready-review receipt changed after lease activation"
    try:
        review = parse_frontmatter(review_path)
    except (OSError, ValueError):
        return None, "Ready-review receipt is invalid"
    if review.get("disposition") != "READY_FOR_IMPLEMENTATION":
        return None, "Ready-review disposition is not READY_FOR_IMPLEMENTATION"
    if review.get("task_id") != lease["task_id"]:
        return None, "Ready-review task ID does not match lease"
    if review.get("task_sha256") != lease["task_sha256"]:
        return None, "Ready-review receipt is not bound to this task revision"
    if review.get("reviewer") != lease.get("approved_by"):
        return None, "Ready-review reviewer does not match approval authority"
    if not isinstance(lease["allowed_paths"], list) or not lease["allowed_paths"]:
        return None, "Lease has no allowed paths"
    if not isinstance(lease["allowed_commands"], list):
        return None, "Lease allowed_commands is invalid"
    return lease, "Active implementation lease is valid"


def parse_frontmatter(path: Path) -> dict[str, Any]:
    """Parse the deliberately small YAML subset used by task contracts."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing YAML frontmatter")
    result: dict[str, Any] = {}
    current_list: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_list:
            result[current_list].append(line[4:].strip().strip('"\''))
            continue
        current_list = None
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            result[key] = []
            current_list = key
        else:
            result[key] = value.strip('"\'')
    return result

#!/usr/bin/env python3
"""Mechanical and adversarial validation for AI Game Development OS v1.2."""

from __future__ import annotations

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


def validate_files(v: Validation) -> None:
    for relative in REQUIRED:
        v.check((ROOT / relative).is_file(), f"missing required file: {relative}")
    v.check(len((ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()) < 200, "CLAUDE.md must remain under 200 lines")
    version = (ROOT / "VERSION").read_text(encoding="utf-8")
    v.check("AI Game Development OS 1.2.0" in version and "Schema: 3" in version, "VERSION must declare v1.2.0 schema 3")
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


def validate_repository_attestation(v: Validation) -> None:
    with tempfile.TemporaryDirectory(prefix="aigdo-attestation-") as temp:
        project = Path(temp) / "project"
        shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
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
        dirty_marker = project / "DIRTY.tmp"
        dirty_marker.write_text("uncommitted\n", encoding="utf-8")
        dirty_activation = subprocess.run(
            [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-TEST-ATTEST.md", "--hours", "1"],
            cwd=project, input="TASK-TEST-ATTEST\nACTIVATE\n", text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        v.check(dirty_activation.returncode == 2, "lease activation must reject a dirty worktree")
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
        shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
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
    v = Validation()
    validate_files(v)
    validate_settings(v)
    validate_frontmatter(v)
    validate_hooks(v)
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

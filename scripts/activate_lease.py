#!/usr/bin/env python3
"""Human-operated activation of a time-limited implementation lease."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS))
from common import git_state, git_worktree_clean, parse_frontmatter  # noqa: E402


UNSAFE_COMMAND = re.compile(r"[\n\r;|><`&]|\$\(")
OPAQUE_COMMAND_START = re.compile(
    r"^(?:bash|sh|zsh|cmd(?:\.exe)?|powershell(?:\.exe)?|pwsh(?:\.exe)?|xargs|env|python(?:3|\.exe)?|py|node(?:\.exe)?)\b",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def inside_project(value: str, label: str) -> tuple[Path, Path]:
    path = (ROOT / value).resolve(strict=False)
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        fail(f"{label} must be inside the project")
    return path, relative


def verify_ssh_approval(review: Path, review_meta: dict[str, object]) -> None:
    required = {"signature_file", "allowed_signers_file"}
    missing = required - set(review_meta)
    if missing:
        fail(f"signed approval missing keys: {', '.join(sorted(missing))}")
    ssh_keygen = shutil.which("ssh-keygen")
    if not ssh_keygen:
        fail("ssh-keygen is required to verify an R4 approval signature")
    signature, _ = inside_project(str(review_meta["signature_file"]), "signature file")
    allowed_signers, _ = inside_project(str(review_meta["allowed_signers_file"]), "allowed signers file")
    if not signature.is_file() or not allowed_signers.is_file():
        fail("signature file or allowed signers file does not exist")
    result = subprocess.run(
        [
            ssh_keygen, "-Y", "verify", "-f", str(allowed_signers),
            "-I", str(review_meta["reviewer"]), "-n", "aigdo-ready-review",
            "-s", str(signature),
        ],
        input=review.read_bytes(), capture_output=True, check=False, timeout=15,
    )
    if result.returncode != 0:
        fail("R4 ready-review SSH signature is invalid or untrusted")


def require_git_tracked(path: Path, label: str) -> None:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative], cwd=ROOT,
        text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=10,
    )
    if result.returncode != 0:
        fail(f"{label} must be tracked in the base Git commit: {relative}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Activate a scoped implementation lease")
    parser.add_argument("task_contract", help="Approved task contract path")
    parser.add_argument("--hours", type=float, default=8.0, help="Lease duration, maximum 24")
    args = parser.parse_args()

    if not 0 < args.hours <= 24:
        fail("--hours must be greater than 0 and at most 24")
    task = (ROOT / args.task_contract).resolve(strict=False)
    try:
        relative_task = task.relative_to(ROOT)
    except ValueError:
        fail("task contract must be inside the project")
    if not task.is_file():
        fail("task contract does not exist")

    meta = parse_frontmatter(task)
    required = {
        "task_id",
        "status",
        "authored_by",
        "approved_by",
        "ready_review_receipt",
        "allowed_paths",
        "allowed_commands",
        "approval_mode",
    }
    missing = required - set(meta)
    if missing:
        fail(f"missing frontmatter keys: {', '.join(sorted(missing))}")
    if meta["status"] != "READY_FOR_IMPLEMENTATION":
        fail("task status must be READY_FOR_IMPLEMENTATION")
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{2,80}", meta["task_id"]):
        fail("task_id must be a bounded uppercase identifier")
    if not meta["approved_by"] or meta["approved_by"] in {"UNSET", "TBD", "implementer"}:
        fail("approved_by must name an independent approval authority")
    if not meta["authored_by"] or meta["authored_by"] in {"UNSET", "TBD"}:
        fail("authored_by must identify the task author")
    if meta["authored_by"].casefold() == meta["approved_by"].casefold():
        fail("task author and independent approval authority must differ")
    if meta["approval_mode"] not in {"hash", "ssh-signature"}:
        fail("approval_mode must be hash or ssh-signature")
    if meta.get("rigor") == "R4" and meta["approval_mode"] != "ssh-signature":
        fail("R4 tasks require approval_mode: ssh-signature")
    if not isinstance(meta["allowed_paths"], list) or not meta["allowed_paths"]:
        fail("allowed_paths must contain at least one scoped path")
    if any(path in {"*", "**", "./**"} for path in meta["allowed_paths"]):
        fail("repository-wide write patterns are forbidden")
    for path in meta["allowed_paths"]:
        normalized = path.replace("\\", "/")
        if normalized.startswith(("/", "~/")) or re.match(r"^[A-Za-z]:", normalized):
            fail(f"allowed path must be project-relative: {path}")
        if "../" in normalized or normalized.startswith(".git/") or normalized.startswith(".ai-governance/"):
            fail(f"allowed path escapes or targets protected state: {path}")
    if not isinstance(meta["allowed_commands"], list):
        fail("allowed_commands must be a list")
    for command in meta["allowed_commands"]:
        if UNSAFE_COMMAND.search(command) or OPAQUE_COMMAND_START.search(command.strip()):
            fail(f"command pattern cannot be safely pre-approved: {command}")
        if re.fullmatch(r"git\s+\*", command.strip(), flags=re.IGNORECASE) or re.match(r"^git\s+-", command.strip(), flags=re.IGNORECASE):
            fail(f"Git command pattern is too broad or uses global execution options: {command}")

    task_digest = sha256(task)
    review = (ROOT / meta["ready_review_receipt"]).resolve(strict=False)
    try:
        relative_review = review.relative_to(ROOT)
    except ValueError:
        fail("ready-review receipt must be inside the project")
    if not review.is_file():
        fail("ready-review receipt does not exist")
    review_meta = parse_frontmatter(review)
    review_required = {
        "review_id", "task_id", "disposition", "reviewer", "task_sha256",
        "reviewed_at", "approval_mode",
    }
    review_missing = review_required - set(review_meta)
    if review_missing:
        fail(f"ready-review receipt missing keys: {', '.join(sorted(review_missing))}")
    if review_meta["disposition"] != "READY_FOR_IMPLEMENTATION":
        fail("ready-review receipt disposition is not READY_FOR_IMPLEMENTATION")
    if review_meta["task_id"] != meta["task_id"]:
        fail("ready-review receipt task ID does not match task contract")
    if review_meta["reviewer"] != meta["approved_by"]:
        fail("ready-review receipt reviewer does not match approved_by")
    if review_meta["task_sha256"] != task_digest:
        fail("ready-review receipt is not bound to the current task-contract hash")
    if review_meta["approval_mode"] != meta["approval_mode"]:
        fail("ready-review approval_mode does not match the task contract")
    if meta["approval_mode"] == "ssh-signature":
        verify_ssh_approval(review, review_meta)

    repository, repository_reason = git_state(ROOT)
    if not repository:
        fail(repository_reason)
    clean, clean_reason = git_worktree_clean(ROOT)
    if not clean:
        fail(clean_reason)
    require_git_tracked(task, "task contract")
    require_git_tracked(review, "ready-review receipt")
    if meta["approval_mode"] == "ssh-signature":
        signature, _ = inside_project(str(review_meta["signature_file"]), "signature file")
        allowed_signers, _ = inside_project(str(review_meta["allowed_signers_file"]), "allowed signers file")
        require_git_tracked(signature, "approval signature")
        require_git_tracked(allowed_signers, "allowed signers file")

    print("\nIMPLEMENTATION LEASE REVIEW")
    print(f"Task:       {meta['task_id']}")
    print(f"Approved:   {meta['approved_by']}")
    print(f"Author:     {meta['authored_by']}")
    print(f"Contract:   {relative_task.as_posix()}")
    print(f"Review:     {relative_review.as_posix()}")
    print(f"Duration:   {args.hours:g} hours")
    print(f"Base HEAD:  {repository['git_head']}")
    print(f"Branch:     {repository['git_branch']}")
    print(f"Approval:   {meta['approval_mode']}")
    print("Allowed paths:")
    for item in meta["allowed_paths"]:
        print(f"  - {item}")
    print("Allowed commands:")
    for item in meta["allowed_commands"] or ["<none; non-read-only commands will ask>"]:
        print(f"  - {item}")

    if input("\nType the exact task ID: ").strip() != meta["task_id"]:
        fail("task ID confirmation failed")
    if input("Type ACTIVATE: ").strip() != "ACTIVATE":
        fail("activation phrase not confirmed")

    now = datetime.now(timezone.utc)
    lease = {
        "schema": 3,
        "state": "ACTIVE",
        "task_id": meta["task_id"],
        "approved_by": meta["approved_by"],
        "authored_by": meta["authored_by"],
        "task_contract": relative_task.as_posix(),
        "task_sha256": task_digest,
        "ready_review_receipt": relative_review.as_posix(),
        "ready_review_sha256": sha256(review),
        "activated_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(hours=args.hours)).isoformat().replace("+00:00", "Z"),
        "allowed_paths": meta["allowed_paths"],
        "allowed_commands": meta["allowed_commands"],
        "approval_mode": meta["approval_mode"],
        **repository,
    }
    destination = ROOT / ".ai-governance" / "implementation-lease.json"
    destination.write_text(json.dumps(lease, indent=2) + "\n", encoding="utf-8")
    print(f"\nACTIVE: {meta['task_id']} until {lease['expires_at']}")


if __name__ == "__main__":
    main()

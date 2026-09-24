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
from common import CONTROLLED_PATHS, git_dirty_paths, git_state, load_owner_policy, matches_any, parse_frontmatter  # noqa: E402
from policy_lib import bump_lease_counter, policy_activation_check  # noqa: E402


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
    parser = argparse.ArgumentParser(description="Activate a scoped implementation lease", allow_abbrev=False)
    parser.add_argument("task_contract", help="Approved task contract path")
    parser.add_argument("--hours", type=float, default=8.0, help="Lease duration, maximum 24")
    parser.add_argument(
        "--inherit-dirty",
        action="store_true",
        help="Accept uncommitted changes that already sit inside the task's allowed_paths",
    )
    parser.add_argument(
        "--owner-policy",
        action="store_true",
        help="Activate under the owner's standing policy (no prompts; the policy checks apply)",
    )
    args = parser.parse_args()

    policy = None
    if args.owner_policy:
        if args.inherit_dirty:
            fail("--inherit-dirty cannot be combined with --owner-policy")
        policy, policy_reason = load_owner_policy(ROOT)
        if policy is None:
            fail(policy_reason)
        if not any(item == "--hours" or item.startswith("--hours=") for item in sys.argv):
            args.hours = float(policy["max_lease_hours"])
        if args.hours > policy["max_lease_hours"]:
            fail(f"--hours exceeds the policy limit of {policy['max_lease_hours']}")
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
    policy_extras: dict = {}
    if policy is not None:
        policy_problems, policy_extras = policy_activation_check(ROOT, policy, meta, review_meta, repository)
        if policy_problems:
            fail("owner-policy activation refused: " + "; ".join(policy_problems))
    dirty, dirty_reason = git_dirty_paths(ROOT)
    if dirty is None:
        fail(dirty_reason)
    protected = {relative_task.as_posix().casefold(), relative_review.as_posix().casefold()}
    if meta["approval_mode"] == "ssh-signature":
        for signature_key in ("signature_file", "allowed_signers_file"):
            protected.add(inside_project(str(review_meta[signature_key]), signature_key)[1].as_posix().casefold())
    tampered = [path for path in dirty if path.casefold() in protected or matches_any(path, CONTROLLED_PATHS)]
    if tampered:
        fail("approved authority and controlled governance files must be committed and unmodified: " + ", ".join(ascii(path) for path in tampered))
    outside = [path for path in dirty if not matches_any(path, meta["allowed_paths"])]
    if outside:
        shown = ", ".join(ascii(path) for path in outside[:5]) + (" ..." if len(outside) > 5 else "")
        fail(f"Git worktree must be clean before lease activation (changes outside allowed_paths: {shown})")
    inherited = dirty
    if inherited and not args.inherit_dirty:
        fail("Git worktree must be clean before lease activation; changes already inside allowed_paths need --inherit-dirty: " + ", ".join(ascii(path) for path in inherited[:5]))
    if len(inherited) > 50:
        fail("too many inherited paths (limit 50)")
    inherited_hashes = {
        path: (sha256(ROOT / path) if (ROOT / path).is_file() else "ABSENT") for path in inherited
    }
    require_git_tracked(task, "task contract")
    require_git_tracked(review, "ready-review receipt")
    if meta["approval_mode"] == "ssh-signature":
        signature, _ = inside_project(str(review_meta["signature_file"]), "signature file")
        allowed_signers, _ = inside_project(str(review_meta["allowed_signers_file"]), "allowed signers file")
        require_git_tracked(signature, "approval signature")
        require_git_tracked(allowed_signers, "allowed signers file")

    existing_lease = ROOT / ".ai-governance" / "implementation-lease.json"
    existing_bytes: bytes | None = None
    existing_state = ""
    existing_task = ""
    if existing_lease.exists():
        try:
            existing_bytes = existing_lease.read_bytes()
            existing = json.loads(existing_bytes.decode("utf-8"))
            existing_state = existing.get("state")
            if not isinstance(existing_state, str):
                raise ValueError("state is not a string")
            existing_task = re.sub(r"[^A-Za-z0-9._-]", "_", str(existing.get("task_id")))[:80]
            if existing_state == "ACTIVE":
                existing_expires = datetime.fromisoformat(str(existing.get("expires_at", "")).replace("Z", "+00:00"))
                if existing_expires.tzinfo is None:
                    raise ValueError("naive expiry")
        except (OSError, ValueError, AttributeError):
            fail("an unreadable implementation lease exists; run scripts/deactivate_lease.py first")
        if existing_state not in {"ACTIVE", "SEALED"}:
            fail(f"an implementation lease in an unknown state exists ({existing_state!r}); run scripts/deactivate_lease.py first")
        if existing_state == "ACTIVE" and existing_expires > datetime.now(timezone.utc):
            fail(f"an unexpired ACTIVE lease exists for {existing_task}; seal or deactivate it first")

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
    if inherited:
        print(f"Changes already in allowed paths ({len(inherited)}; will be part of the sealed diff):")
        for item in inherited:
            print(f"  - {ascii(item)}")

    if policy is None:
        if input("\nType the exact task ID: ").strip() != meta["task_id"]:
            fail("task ID confirmation failed")
        if input("Type ACTIVATE: ").strip() != "ACTIVATE":
            fail("activation phrase not confirmed")

    now = datetime.now(timezone.utc)
    if existing_bytes is not None:
        archive_dir = ROOT / ".ai-governance" / "implementation-seals"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive = archive_dir / f"PRIOR-{existing_task}-{existing_state}-{now.strftime('%Y%m%dT%H%M%S%fZ')}.json"
        with archive.open("xb") as archive_handle:
            archive_handle.write(existing_bytes)
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
        "inherited_paths": inherited_hashes,
        "authority": "owner-policy" if policy is not None else "human",
        **policy_extras,
        **repository,
    }
    destination = ROOT / ".ai-governance" / "implementation-lease.json"
    destination.write_text(json.dumps(lease, indent=2) + "\n", encoding="utf-8")
    if policy is not None:
        bump_lease_counter(ROOT)
    print(f"\nACTIVE: {meta['task_id']} until {lease['expires_at']}")


if __name__ == "__main__":
    main()

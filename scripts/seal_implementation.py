#!/usr/bin/env python3
"""Human-operated sealing of the exact implementation diff."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
from common import file_sha256, load_lease, matches_any  # noqa: E402


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=False, timeout=30,
    )
    if result.returncode != 0:
        raise SystemExit(f"ERROR: git {' '.join(args)} failed")
    return result.stdout


def changed_paths() -> list[str]:
    groups = (
        git_bytes("diff", "--name-only", "-z", "HEAD"),
        git_bytes("ls-files", "--others", "--exclude-standard", "-z"),
    )
    return sorted({item.decode("utf-8") for group in groups for item in group.split(b"\0") if item})


def main() -> None:
    lease, reason = load_lease(ROOT)
    if not lease:
        raise SystemExit(f"ERROR: {reason}")
    paths = changed_paths()
    if not paths:
        raise SystemExit("ERROR: there is no implementation diff to seal")
    outside = [path for path in paths if not matches_any(path, lease["allowed_paths"])]
    if outside:
        raise SystemExit("ERROR: changed paths outside lease: " + ", ".join(outside))

    digest = hashlib.sha256()
    digest.update(b"AIGDO-IMPLEMENTATION-DIFF-V1\0")
    digest.update(lease["git_head"].encode("ascii") + b"\0")
    digest.update(git_bytes("diff", "--binary", "--no-ext-diff", "HEAD"))
    untracked = set(git_bytes("ls-files", "--others", "--exclude-standard", "-z").split(b"\0"))
    untracked_hashes: dict[str, str] = {}
    for path in paths:
        encoded = path.encode("utf-8")
        if encoded in untracked:
            value = file_sha256(ROOT / path)
            untracked_hashes[path] = value
            digest.update(b"UNTRACKED\0" + encoded + b"\0" + value.encode("ascii") + b"\0")

    seal = {
        "schema": 1,
        "state": "SEALED",
        "task_id": lease["task_id"],
        "task_sha256": lease["task_sha256"],
        "ready_review_sha256": lease["ready_review_sha256"],
        "base_git_head": lease["git_head"],
        "git_branch": lease["git_branch"],
        "changed_paths": paths,
        "diff_sha256": digest.hexdigest(),
        "untracked_file_sha256": untracked_hashes,
        "sealed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    seal_dir = ROOT / ".ai-governance" / "implementation-seals"
    seal_dir.mkdir(parents=True, exist_ok=True)
    seal_name = f"{lease['task_id']}-{lease['task_sha256'][:12]}-{lease['git_head'][:12]}.json"
    seal_path = seal_dir / seal_name
    if seal_path.exists():
        raise SystemExit(f"ERROR: immutable implementation seal already exists: {seal_path.relative_to(ROOT)}")
    seal_path.write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    seal_sha = file_sha256(seal_path)
    lease["state"] = "SEALED"
    lease["implementation_seal"] = seal_path.relative_to(ROOT).as_posix()
    lease["implementation_seal_sha256"] = seal_sha
    (ROOT / ".ai-governance" / "implementation-lease.json").write_text(
        json.dumps(lease, indent=2) + "\n", encoding="utf-8"
    )
    print(f"SEALED: {lease['task_id']}")
    print(f"Diff SHA-256: {seal['diff_sha256']}")
    print(f"Seal SHA-256: {seal_sha}")
    print(f"Seal: {seal_path.relative_to(ROOT).as_posix()}")
    print("Further agent writes are now blocked.")


if __name__ == "__main__":
    main()

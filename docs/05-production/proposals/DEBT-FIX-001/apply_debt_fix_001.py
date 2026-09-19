#!/usr/bin/env python3
"""PROPOSED patch applier for DEBT-FIX-001 (DEBT-002, DEBT-003, DEBT-006). Human-run only.

Dry run by default: checks that every old snippet occurs exactly once and that the patched
Python still compiles, then prints the plan. Nothing is written without --apply, and --apply
needs an interactive terminal. Only the five listed target files can be edited.
Verify this file's SHA-256 against the value recorded in DEBT-FIX-001.md before running it.
Revert with `git restore <files>` before committing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

ALLOWED_TARGETS = frozenset(
    {
        ".claude/hooks/common.py",
        "scripts/activate_lease.py",
        "scripts/seal_implementation.py",
        "scripts/validate_os.py",
        "scripts/doctor.py",
    }
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str) -> None:
    EDITS.append((path, old, new))


COPY_IGNORE = (
    'ignore=shutil.ignore_patterns(\n'
    '                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",\n'
    '            ),\n'
)

# --- .claude/hooks/common.py: read every dirty path (DEBT-003) -------------------------------
edit(
    ".claude/hooks/common.py",
    r'''def load_lease(root: Path) -> tuple[dict[str, Any] | None, str]:
''',
    r'''def git_dirty_paths(root: Path) -> tuple[list[str] | None, str]:
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


def load_lease(root: Path) -> tuple[dict[str, Any] | None, str]:
''',
)

# --- scripts/activate_lease.py --------------------------------------------------------------
edit(
    "scripts/activate_lease.py",
    r'''from common import git_state, git_worktree_clean, parse_frontmatter  # noqa: E402''',
    r'''from common import CONTROLLED_PATHS, git_dirty_paths, git_state, matches_any, parse_frontmatter  # noqa: E402''',
)
# DEBT-003: dirty paths inside allowed_paths may be inherited, but never the approved authority files.
edit(
    "scripts/activate_lease.py",
    r'''    clean, clean_reason = git_worktree_clean(ROOT)
    if not clean:
        fail(clean_reason)
''',
    r'''    dirty, dirty_reason = git_dirty_paths(ROOT)
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
''',
)
# DEBT-002: refuse to overwrite a live lease (checked before any prompt).
edit(
    "scripts/activate_lease.py",
    r'''    print("\nIMPLEMENTATION LEASE REVIEW")''',
    r'''    existing_lease = ROOT / ".ai-governance" / "implementation-lease.json"
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

    print("\nIMPLEMENTATION LEASE REVIEW")''',
)
edit(
    "scripts/activate_lease.py",
    r'''    for item in meta["allowed_commands"] or ["<none; non-read-only commands will ask>"]:
        print(f"  - {item}")
''',
    r'''    for item in meta["allowed_commands"] or ["<none; non-read-only commands will ask>"]:
        print(f"  - {item}")
    if inherited:
        print(f"Changes already in allowed paths ({len(inherited)}; will be part of the sealed diff):")
        for item in inherited:
            print(f"  - {ascii(item)}")
''',
)
edit(
    "scripts/activate_lease.py",
    r'''    parser.add_argument("--hours", type=float, default=8.0, help="Lease duration, maximum 24")
    args = parser.parse_args()
''',
    r'''    parser.add_argument("--hours", type=float, default=8.0, help="Lease duration, maximum 24")
    parser.add_argument(
        "--inherit-dirty",
        action="store_true",
        help="Accept uncommitted changes that already sit inside the task's allowed_paths",
    )
    args = parser.parse_args()
''',
)
edit(
    "scripts/seal_implementation.py",
    r'''        git_bytes("diff", "--name-only", "-z", "HEAD"),
''',
    r'''        git_bytes("diff", "--name-only", "--no-renames", "-z", "HEAD"),
''',
)
# DEBT-002: archive the prior lease only after the human has confirmed the new one (never overwrite an archive).
edit(
    "scripts/activate_lease.py",
    r'''    now = datetime.now(timezone.utc)
    lease = {
''',
    r'''    now = datetime.now(timezone.utc)
    if existing_bytes is not None:
        archive_dir = ROOT / ".ai-governance" / "implementation-seals"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive = archive_dir / f"PRIOR-{existing_task}-{existing_state}-{now.strftime('%Y%m%dT%H%M%S%fZ')}.json"
        with archive.open("xb") as archive_handle:
            archive_handle.write(existing_bytes)
    lease = {
''',
)
edit(
    "scripts/activate_lease.py",
    r'''        **repository,
    }
''',
    r'''        "inherited_paths": inherited_hashes,
        **repository,
    }
''',
)

# --- scripts/seal_implementation.py: carry inherited paths into the seal (DEBT-003 audit) -----
edit(
    "scripts/seal_implementation.py",
    r'''        "untracked_file_sha256": untracked_hashes,
''',
    r'''        "untracked_file_sha256": untracked_hashes,
        "inherited_paths": lease.get("inherited_paths", {}),
''',
)

# --- scripts/validate_os.py: working-repository mode, copy exclusions, tests -----------------
edit(
    "scripts/validate_os.py",
    r'''import hashlib
import json
''',
    r'''import argparse
import hashlib
import json
''',
)
edit(
    "scripts/validate_os.py",
    r'''def validate_files(v: Validation) -> None:''',
    r'''def validate_files(v: Validation, working_repository: bool = False) -> None:''',
)
edit(
    "scripts/validate_os.py",
    r'''    v.check(not (ROOT / ".ai-governance" / "implementation-lease.json").exists(), "deliverable must not contain an active implementation lease")
    seal_dir = ROOT / ".ai-governance" / "implementation-seals"
    v.check(not seal_dir.exists() or not any(seal_dir.iterdir()), "deliverable must not contain an implementation seal")
''',
    r'''    if working_repository:
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
''',
)
edit(
    "scripts/validate_os.py",
    r'''        project = Path(temp) / "project"
        shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))''',
    "        project = Path(temp) / \"project\"\n        shutil.copytree(\n            ROOT, project,\n            " + COPY_IGNORE + "        )",
)
edit(
    "scripts/validate_os.py",
    r'''        project = root / "r4-project"
        shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))''',
    "        project = root / \"r4-project\"\n        shutil.copytree(\n            ROOT, project,\n            " + COPY_IGNORE + "        )",
)
edit(
    "scripts/validate_os.py",
    r'''        dirty_marker = project / "DIRTY.tmp"''',
    r'''        def activate_attest_task(*extra: str) -> subprocess.CompletedProcess[str]:
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
        dirty_marker = project / "DIRTY.tmp"''',
)
edit(
    "scripts/validate_os.py",
    r'''        v.check(dirty_activation.returncode == 2, "lease activation must reject a dirty worktree")
''',
    r'''        v.check(dirty_activation.returncode == 2, "lease activation must reject a dirty worktree")
        v.check("DIRTY.tmp" in dirty_activation.stderr, "dirty-worktree rejection must name the offending path")
''',
)
edit(
    "scripts/validate_os.py",
    r'''        (source / "X.cpp").write_text("int attested = 1;\n", encoding="utf-8")''',
    r'''        second_activation = activate_attest_task()
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
        (source / "X.cpp").write_text("int attested = 1;\n", encoding="utf-8")''',
)
edit(
    "scripts/validate_os.py",
    r'''def main() -> None:
    v = Validation()
    validate_files(v)
''',
    r'''def main() -> None:
    parser = argparse.ArgumentParser(description="Mechanical and adversarial validation")
    parser.add_argument(
        "--working-repository",
        action="store_true",
        help="Skip the package-only checks that reject a local lease or implementation seals",
    )
    args = parser.parse_args()
    v = Validation()
    validate_files(v, args.working_repository)
''',
)

# --- scripts/doctor.py: pass the flag through --------------------------------------------------
edit(
    "scripts/doctor.py",
    r'''    parser.add_argument("--require-claude", action="store_true", help="Fail when the Claude Code executable is unavailable")
    args = parser.parse_args()''',
    r'''    parser.add_argument("--require-claude", action="store_true", help="Fail when the Claude Code executable is unavailable")
    parser.add_argument("--working-repository", action="store_true", help="Run the validator without its package-only lease and seal checks")
    args = parser.parse_args()''',
)
edit(
    "scripts/doctor.py",
    r'''        [sys.executable, str(ROOT / "scripts" / "validate_os.py")],''',
    r'''        [sys.executable, str(ROOT / "scripts" / "validate_os.py"), *(["--working-repository"] if args.working_repository else [])],''',
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
    print("Applied. Now read `git diff` for these files and run the verification steps in DEBT-FIX-001.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

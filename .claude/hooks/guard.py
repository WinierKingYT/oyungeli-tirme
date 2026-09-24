#!/usr/bin/env python3
"""v3 guard hook (PreToolUse).

Blocks only hard-to-reverse mistakes in a Unity project; everything else passes.
Decisions are returned as Claude Code hook JSON on stdout.
"""
from __future__ import annotations

import json
import re
import sys
from fnmatch import fnmatch
from pathlib import PurePosixPath

# Unity serialized files must be changed through the Editor / Unity MCP, never as text.
DENY_WRITE_PATTERNS = (
    "*.meta",
    "*.unity",
    "*.prefab",
    "*.asset",
    "*.controller",
    "*.anim",
    "*.mat",
)

# Allowed, but the owner confirms first.
ASK_WRITE_PATTERNS = (
    "ProjectSettings/*",
    "Packages/manifest.json",
    "Packages/packages-lock.json",
    ".claude/settings.json",
    ".claude/hooks/*",
)

DENY_SHELL = (
    (re.compile(r"\bgit\s+push\b"), "git push is done by the owner"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "git reset --hard discards work"),
    (re.compile(r"\bgit\s+clean\s+-[a-z]*f"), "git clean -f deletes untracked files"),
    (re.compile(r"\bgit\s+checkout\s+--\s"), "git checkout -- discards changes"),
    (re.compile(r"\bgit\s+(rebase|filter-branch)\b"), "history rewrite is done by the owner"),
    (re.compile(r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r"), "recursive force delete"),
    (re.compile(r"Remove-Item\b.*-Recurse", re.IGNORECASE), "recursive delete"),
)

DELETE_PROTECTED = re.compile(
    r"(rm|del|Remove-Item|rmdir)\b.*\b(Assets|ProjectSettings|Packages)\b", re.IGNORECASE
)


def decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def normalize(path: str, cwd: str) -> str:
    p = path.replace("\\", "/")
    root = cwd.replace("\\", "/").rstrip("/") + "/"
    if p.lower().startswith(root.lower()):
        p = p[len(root):]
    while p.startswith("./"):
        p = p[2:]
    return p


def matches(path: str, patterns: tuple[str, ...]) -> str | None:
    name = PurePosixPath(path).name
    for pattern in patterns:
        if fnmatch(path, pattern) or fnmatch(name, pattern):
            return pattern
    return None


def check_write(tool_input: dict, cwd: str) -> None:
    raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    path = normalize(raw, cwd)
    if not path:
        return
    hit = matches(path, DENY_WRITE_PATTERNS)
    if hit:
        decide("deny", f"{path}: Unity serialized file ({hit}). Use Unity MCP / Editor APIs instead of text edits.")
    hit = matches(path, ASK_WRITE_PATTERNS)
    if hit:
        decide("ask", f"{path}: project-wide setting ({hit}); confirm with the owner.")


def check_shell(tool_input: dict) -> None:
    command = tool_input.get("command", "")
    for pattern, reason in DENY_SHELL:
        if pattern.search(command):
            decide("deny", f"Blocked: {reason}.")
    if DELETE_PROTECTED.search(command):
        decide("ask", "Deleting inside Assets/ProjectSettings/Packages; confirm with the owner.")


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"guard.py: unreadable hook input ({exc}); allowing", file=sys.stderr)
        sys.exit(0)

    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd", "")

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        check_write(tool_input, cwd)
    elif tool in ("Bash", "PowerShell"):
        check_shell(tool_input)
    sys.exit(0)


if __name__ == "__main__":
    main()

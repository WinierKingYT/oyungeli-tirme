#!/usr/bin/env python3
"""Runtime preflight for the AI Game Development OS control plane."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight the AI Game Development OS runtime")
    parser.add_argument("--require-claude", action="store_true", help="Fail when the Claude Code executable is unavailable")
    args = parser.parse_args()
    failures: list[str] = []
    warnings: list[str] = []
    if sys.version_info < (3, 10):
        failures.append("Python 3.10+ is required")

    settings_path = ROOT / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"settings.json is unreadable: {exc}")
        settings = {}
    permissions = settings.get("permissions", {})
    if permissions.get("defaultMode") != "plan":
        failures.append("defaultMode is not plan")
    if permissions.get("disableBypassPermissionsMode") != "disable":
        failures.append("bypassPermissions mode is not disabled")
    if permissions.get("disableAutoMode") != "disable":
        failures.append("auto mode is not disabled")
    pre_tool = settings.get("hooks", {}).get("PreToolUse", [])
    matchers = {entry.get("matcher") for entry in pre_tool}
    if "^mcp__.*$" not in matchers:
        failures.append("MCP governance hook is not registered")
    if not settings.get("hooks", {}).get("ConfigChange"):
        failures.append("ConfigChange hardening hook is not registered")
    try:
        policy = json.loads((ROOT / ".ai-governance" / "mcp-policy.json").read_text(encoding="utf-8"))
        if policy.get("schema") != 1:
            failures.append("MCP policy schema is invalid")
    except Exception as exc:
        failures.append(f"MCP policy is unreadable: {exc}")

    git = shutil.which("git")
    if not git:
        failures.append("Git executable was not found on PATH")
    else:
        repository = subprocess.run(
            [git, "rev-parse", "--show-toplevel"], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        if repository.returncode != 0 or Path(repository.stdout.strip()).resolve() != ROOT.resolve():
            message = "package must be installed at the Git repository root"
            if args.require_claude:
                failures.append(message)
            else:
                warnings.append(message + "; strict runtime preflight will fail until installed")

    claude = shutil.which("claude")
    if not claude:
        message = "Claude Code executable was not found on PATH"
        if args.require_claude:
            failures.append(message)
        else:
            warnings.append(message + "; run again with --require-claude in the actual developer environment")
    else:
        completed = subprocess.run([claude, "--version"], text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            warnings.append("Claude Code version could not be queried")

    hook = ROOT / ".claude" / "hooks" / "govern_write.py"
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "cwd": str(ROOT),
        "tool_input": {"file_path": str(ROOT / "Source" / "Probe.cpp")},
    }
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    env["AIGDO_TEST_FORCE_ERROR"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    probe = subprocess.run(
        [sys.executable, str(hook)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if probe.returncode != 2:
        failures.append("hook exception probe did not fail closed with exit code 2")

    validation = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_os.py")],
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    if validation.returncode != 0:
        failures.append("mechanical validator failed")

    print(f"Python: {sys.version.split()[0]}")
    print(f"Claude Code: {claude or 'NOT FOUND'}")
    print(f"Git: {git or 'NOT FOUND'}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("RESULT: FAIL")
        raise SystemExit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Block controlled or out-of-scope file writes before Claude executes them."""

from __future__ import annotations

from common import (
    ALWAYS_DOCUMENTATION_PATHS,
    CONTROLLED_PATHS,
    load_lease,
    matches_any,
    project_root,
    read_hook_input,
    relative_target,
    emit_decision,
    run_fail_closed,
    working_root,
)


def main() -> None:
    data = read_hook_input()
    tool_input = data.get("tool_input", {})
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(target, str) or not target:
        emit_decision(data, "deny", "Write target is missing; fail closed")
        return

    cwd = working_root(data)
    relative = relative_target(target, cwd)
    if relative is None:
        emit_decision(data, "deny", "Writes outside the active working tree are not allowed")
        return
    if matches_any(relative, CONTROLLED_PATHS):
        emit_decision(data, "deny", f"Governance-controlled path cannot be modified by an agent: {relative}")
        return

    lease, lease_reason = load_lease(project_root())
    if lease and matches_any(relative, lease["allowed_paths"]):
        emit_decision(data, "allow", f"Path is inside active task {lease['task_id']}: {relative}")
        return

    if matches_any(relative, ALWAYS_DOCUMENTATION_PATHS):
        emit_decision(
            data,
            "ask",
            f"Documentation write is outside an active implementation lease: {relative}",
            "Confirm that this is documentation-only and does not alter production behavior.",
        )
        return

    emit_decision(
        data,
        "deny",
        f"LEASE_REQUIRED: {relative} is not authorized. {lease_reason}",
        "Create and independently approve a task contract, then have the human activate its lease outside Claude.",
    )


if __name__ == "__main__":
    run_fail_closed(main)

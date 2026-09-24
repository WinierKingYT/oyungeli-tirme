#!/usr/bin/env python3
"""Gate every MCP tool because MCP can mutate state outside filesystem hooks."""

from __future__ import annotations

import json

from common import emit_decision, load_lease, project_root, read_hook_input, run_fail_closed


def main() -> None:
    data = read_hook_input()
    tool_name = data.get("tool_name")
    if not isinstance(tool_name, str) or not tool_name.startswith("mcp__"):
        emit_decision(data, "deny", "Malformed MCP tool event; fail closed")
        return

    policy_path = project_root() / ".ai-governance" / "mcp-policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        emit_decision(data, "deny", "MCP policy is missing or invalid; fail closed")
        return

    no_lease = policy.get("allow_without_lease", [])
    with_lease = policy.get("allow_with_lease", [])
    if not isinstance(no_lease, list) or not isinstance(with_lease, list):
        emit_decision(data, "deny", "MCP policy lists are invalid; fail closed")
        return
    if tool_name in no_lease:
        emit_decision(data, "allow", "Exact MCP tool is allowlisted for read-only use")
        return

    lease, reason = load_lease(project_root())
    if not lease:
        emit_decision(data, "deny", f"LEASE_REQUIRED: MCP tool blocked. {reason}")
        return
    if tool_name in with_lease:
        emit_decision(data, "allow", f"Exact MCP tool is authorized by task {lease['task_id']}")
        return
    emit_decision(
        data,
        "ask",
        f"MCP tool is not pre-authorized by task {lease['task_id']}",
        "MCP tools may mutate remote systems; inspect the full tool input before one-time approval.",
    )


if __name__ == "__main__":
    run_fail_closed(main)

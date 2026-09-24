#!/usr/bin/env python3
"""v3 feedback hook (PostToolUse).

After a C# edit: reminds the agent of the verification ladder, and warns when a
serialized field appears to be removed or renamed (silent data loss in Unity).
After a Unity bridge write: reminds it to check the console and, for visual
changes, to look at the result once the batch of edits is done.
Never blocks.
"""
from __future__ import annotations

import json
import re
import sys

CS_REMINDER = (
    "C# changed. Verification ladder: pick the lowest rung that can catch a mistake here — "
    "EditMode test for rules, compile status (MCP or offline dotnet build, ~3 s) for all edits, "
    "PlayMode/screenshot for behavior or visuals. Show the evidence before calling it done."
)
SERIALIZED_WARNING = (
    "Serialized field(s) removed or renamed: {names}. Unity silently drops their saved values. "
    "Use [FormerlySerializedAs(\"old\")] for renames and tell the owner about removals."
)
MCP_WRITE_REMINDER = (
    "Unity content changed through the bridge. Batch related edits, then verify once: "
    "read the console, and for visual changes capture a screenshot and compare with the card."
)
MCP_WRITE_HINTS = ("create", "add", "set", "update", "modify", "delete", "move", "instantiate",
                   "execute", "run", "save")

SERIALIZED_FIELD = re.compile(
    r"\[SerializeField\][^;\n]*?\b(\w+)\s*(?:=|;)|public\s+(?!static|const|readonly)[\w<>\[\],\s]+?\s+(\w+)\s*(?:=[^;]*)?;"
)


def context(text: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}
    }))


def field_names(code: str) -> set[str]:
    return {a or b for a, b in SERIALIZED_FIELD.findall(code or "")}


def removed_serialized_fields(tool_input: dict) -> set[str]:
    edits = tool_input.get("edits") or [tool_input]
    removed: set[str] = set()
    for edit in edits:
        before = field_names(edit.get("old_string", ""))
        after = field_names(edit.get("new_string", ""))
        removed |= before - after
    return removed


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    messages: list[str] = []

    if tool in ("Write", "Edit", "MultiEdit"):
        if str(tool_input.get("file_path", "")).lower().endswith(".cs"):
            messages.append(CS_REMINDER)
            if tool in ("Edit", "MultiEdit"):
                removed = removed_serialized_fields(tool_input)
                if removed:
                    messages.append(SERIALIZED_WARNING.format(names=", ".join(sorted(removed))))
    elif tool.startswith("mcp__") and "unity" in tool.lower():
        action = tool.rsplit("__", 1)[-1].lower()
        if any(hint in action for hint in MCP_WRITE_HINTS):
            messages.append(MCP_WRITE_REMINDER)

    if messages:
        context(" ".join(messages))
    sys.exit(0)


if __name__ == "__main__":
    main()

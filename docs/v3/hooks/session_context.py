#!/usr/bin/env python3
"""v3 session hook (SessionStart and PreCompact).

SessionStart: injects memory/STATE.md and warns about gaps (C# features without a
system card, open judgement gaps).
PreCompact: reminds the agent to rewrite memory/STATE.md before context is compacted,
so progress survives compaction.
Never blocks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

STATE_FILE = Path("memory/STATE.md")
CARDS_DIR = Path("game/systems")
SCRIPTS_DIR = Path("Assets/_Project/Scripts")
GAPS_FILE = Path("game/JUDGMENT-GAPS.md")
MAX_STATE_CHARS = 4000
IGNORED_FEATURE_DIRS = {"Core", "Editor", "Tools"}


def emit(event_name: str, text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": text}}))


def features_without_cards(root: Path) -> list[str]:
    scripts = root / SCRIPTS_DIR
    cards = root / CARDS_DIR
    if not scripts.is_dir():
        return []
    card_text = " ".join(p.read_text(encoding="utf-8", errors="replace").lower()
                         for p in cards.glob("*.md")) if cards.is_dir() else ""
    return sorted(d.name for d in scripts.iterdir()
                  if d.is_dir() and d.name not in IGNORED_FEATURE_DIRS and d.name.lower() not in card_text)


def open_gaps(root: Path) -> int:
    path = root / GAPS_FILE
    if not path.is_file():
        return 0
    rows = [line for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.startswith("|") and not line.startswith("|---") and "Question" not in line]
    return sum(1 for row in rows if len(row.split("|")) > 3 and not row.split("|")[3].strip())


def session_start(root: Path) -> None:
    parts: list[str] = []
    state = root / STATE_FILE
    if state.is_file():
        parts.append("memory/STATE.md:\n" + state.read_text(encoding="utf-8", errors="replace")[:MAX_STATE_CHARS])
    else:
        parts.append("memory/STATE.md does not exist yet; create it at the end of this session.")
    missing = features_without_cards(root)
    if missing:
        parts.append("Code folders without a system card: " + ", ".join(missing) +
                     ". Consider `/design-system` quick mode to document them.")
    gaps = open_gaps(root)
    if gaps:
        parts.append(f"{gaps} judgement gap(s) unanswered in game/JUDGMENT-GAPS.md — ask instead of deciding.")
    emit("SessionStart", "\n\n".join(parts))


def pre_compact() -> None:
    emit("PreCompact", "Context is about to be compacted. Rewrite memory/STATE.md now "
                       "(Now / Last session / Next / Open questions / Watch out) so progress survives.")


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    name = event.get("hook_event_name", "")
    root = Path(event.get("cwd") or ".")
    try:
        if name == "SessionStart":
            session_start(root)
        elif name == "PreCompact":
            pre_compact()
    except OSError as exc:
        print(f"session_context.py: {exc}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()

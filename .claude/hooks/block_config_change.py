#!/usr/bin/env python3
"""Prevent live weakening of project settings, local settings, or skills."""

from __future__ import annotations

import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
        source = data.get("source", "unknown")
        if source == "policy_settings":
            return
        print(json.dumps({
            "decision": "block",
            "reason": f"Live {source} changes are blocked; review and restart the session.",
        }))
    except BaseException as exc:
        print(f"ConfigChange policy failed closed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()

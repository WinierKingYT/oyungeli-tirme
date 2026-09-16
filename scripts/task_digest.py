#!/usr/bin/env python3
"""Print the canonical SHA-256 used to bind a ready-review receipt."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash one project task contract")
    parser.add_argument("task_contract")
    args = parser.parse_args()
    target = (ROOT / args.task_contract).resolve(strict=False)
    try:
        relative = target.relative_to(ROOT)
    except ValueError:
        raise SystemExit("Task contract must be inside the project")
    if not target.is_file():
        raise SystemExit("Task contract does not exist")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"{digest}  {relative.as_posix()}")


if __name__ == "__main__":
    main()


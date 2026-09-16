#!/usr/bin/env python3
"""Hash one evidence file or directory with deterministic path ordering."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    files = sorted(item for item in path.rglob("*") if item.is_file())
    for item in files:
        relative = item.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content_hash = bytes.fromhex(file_digest(item))
        digest.update(content_hash)
    return digest.hexdigest(), len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash one project evidence artifact")
    parser.add_argument("artifact")
    args = parser.parse_args()
    target = (ROOT / args.artifact).resolve(strict=False)
    try:
        relative = target.relative_to(ROOT)
    except ValueError:
        raise SystemExit("Artifact must be inside the project")
    if target.is_file():
        print(f"{file_digest(target)}  file  {relative.as_posix()}")
        return
    if target.is_dir():
        digest, count = tree_digest(target)
        print(f"{digest}  tree:{count}  {relative.as_posix()}")
        return
    raise SystemExit("Artifact does not exist")


if __name__ == "__main__":
    main()


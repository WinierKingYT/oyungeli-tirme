#!/usr/bin/env python3
"""Verify an SSH-signed approval receipt without accessing a private key."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("signature", type=Path)
    parser.add_argument("allowed_signers", type=Path)
    parser.add_argument("identity")
    args = parser.parse_args()
    executable = shutil.which("ssh-keygen")
    if not executable:
        raise SystemExit("ERROR: ssh-keygen is not installed")
    result = subprocess.run(
        [
            executable, "-Y", "verify", "-f", str(args.allowed_signers),
            "-I", args.identity, "-n", "aigdo-ready-review",
            "-s", str(args.signature),
        ],
        input=args.receipt.read_bytes(), check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

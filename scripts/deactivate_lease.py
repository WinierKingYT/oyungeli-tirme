#!/usr/bin/env python3
"""Human-operated lease removal."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEASE = ROOT / ".ai-governance" / "implementation-lease.json"

if not LEASE.exists():
    print("Implementation lease is already inactive.")
else:
    confirmation = input("Type DEACTIVATE to remove the active lease: ").strip()
    if confirmation != "DEACTIVATE":
        raise SystemExit("Canceled.")
    LEASE.unlink()
    print("Implementation lease deactivated.")


# Technical Debt Register

| ID | Debt | Cause | Interest | Remediation trigger | Owner | State |
|---|---|---|---|---|---|---|
| DEBT-001 | `scripts/doctor.py --require-claude` strict preflight (`doctor.py:57-61`) reports "package must be installed at the Git repository root" even when correctly installed, whenever the repository path contains non-ASCII characters (e.g. Turkish "ş") on Windows | `subprocess.run(..., text=True)` does not pass `encoding="utf-8"`, so git's UTF-8 `rev-parse --show-toplevel` output can decode differently from `Path(__file__).resolve()` on Windows, breaking the string/path equality check | Every non-ASCII-path Windows install fails strict preflight even when correctly installed at the Git root, undermining confidence in the one check meant to catch this class of misconfiguration | Fix before strict preflight is relied on for a real R1+ task on a non-ASCII path, or before onboarding docs recommend Windows-native installs | Tech owner | Open |

Debt is an explicit trade-off, not a label for every imperfection. Record why it exists, what it costs, and when it must be paid.


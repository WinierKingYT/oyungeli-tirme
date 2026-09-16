# Risk Register

| ID | Risk | Likelihood | Impact | Detection | Mitigation | Owner | State |
|---|---|---:|---:|---|---|---|---|
| RISK-001 | Bootstrap assumptions do not match the actual repository | High | High | Project discovery | Do not implement before discovery | Project owner | Open |
| RISK-002 | Hook runtime unavailable on a developer machine | Medium | High | Validator/startup | Install Python 3.10+; CI check | Tech owner | Open |
| RISK-003 | Agent uses shell indirection outside hook pattern coverage | Low/Medium | High | Review/audit | Plan mode, manual permissions, sandbox/branch protection | Tech owner | Open |
| RISK-004 | Process becomes too heavy for trivial work | Medium | Medium | Cycle-time review | Use rigor levels R0–R4 | Project owner | Open |
| RISK-005 | Documentation claims outrun evidence | Medium | High | Drift audit | Independent review and lifecycle vocabulary | Docs owner | Open |
| RISK-006 | **ESCALATED 2026-09-16 — High/High, not Medium/Medium.** The same non-ASCII-path bug (DEBT-001) exists in `.claude/hooks/common.py:git_state()`, which `scripts/activate_lease.py` and every governed hook's `load_lease()` depend on — confirmed by a real, failed `activate_lease.py` run on this repository (`ERROR: AI Game Development OS must be installed at the Git repository root`). This is a full functional block on lease activation on this machine, not a false-positive warning | High | High | Observed directly on 2026-09-16: first via `doctor.py --require-claude`, then confirmed via a genuine failed `activate_lease.py` invocation | Pass explicit `encoding="utf-8"` in every `subprocess.run` call in both `scripts/doctor.py` and `.claude/hooks/common.py`; add a non-ASCII-path case to `validate_os.py`'s adversarial suite so this class of bug is caught before packaging, not discovered live | Tech owner (human-only fix — both files are `CONTROLLED_PATHS`) | Open |


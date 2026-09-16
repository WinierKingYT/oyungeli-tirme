# Risk Register

| ID | Risk | Likelihood | Impact | Detection | Mitigation | Owner | State |
|---|---|---:|---:|---|---|---|---|
| RISK-001 | Bootstrap assumptions do not match the actual repository | High | High | Project discovery | Do not implement before discovery | Project owner | Open |
| RISK-002 | Hook runtime unavailable on a developer machine | Medium | High | Validator/startup | Install Python 3.10+; CI check | Tech owner | Open |
| RISK-003 | Agent uses shell indirection outside hook pattern coverage | Low/Medium | High | Review/audit | Plan mode, manual permissions, sandbox/branch protection | Tech owner | Open |
| RISK-004 | Process becomes too heavy for trivial work | Medium | Medium | Cycle-time review | Use rigor levels R0–R4 | Project owner | Open |
| RISK-005 | Documentation claims outrun evidence | Medium | High | Drift audit | Independent review and lifecycle vocabulary | Docs owner | Open |
| RISK-006 | Strict runtime preflight (`doctor.py --require-claude`) reports false-positive failures on valid installs when the repository path contains non-ASCII characters on Windows (see DEBT-001) | Medium | Medium | Observed directly on 2026-09-16 during Git bring-up verification | Pass explicit `encoding="utf-8"` in `doctor.py`'s subprocess call and normalize both paths before comparison; add a non-ASCII-path case to `validate_os.py`'s adversarial suite | Tech owner | Open |


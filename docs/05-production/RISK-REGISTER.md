# Risk Register

| ID | Risk | Likelihood | Impact | Detection | Mitigation | Owner | State |
|---|---|---:|---:|---|---|---|---|
| RISK-001 | Bootstrap assumptions do not match the actual repository | High | High | Project discovery | Do not implement before discovery | Project owner | Open |
| RISK-002 | Hook runtime unavailable on a developer machine | Medium | High | Validator/startup | Install Python 3.10+; CI check | Tech owner | Open |
| RISK-003 | Agent uses shell indirection outside hook pattern coverage | Low/Medium | High | Review/audit | Plan mode, manual permissions, sandbox/branch protection | Tech owner | Open |
| RISK-004 | Process becomes too heavy for trivial work | Medium | Medium | Cycle-time review | Use rigor levels R0–R4 | Project owner | Open |
| RISK-005 | Documentation claims outrun evidence | Medium | High | Drift audit | Independent review and lifecycle vocabulary | Docs owner | Open |


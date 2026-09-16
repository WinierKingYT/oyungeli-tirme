# Quality Model

Every system selects and ranks applicable quality attributes:

| Attribute | Required question |
|---|---|
| Correctness | Does state and behavior match the contract? |
| Reliability | Does it remain valid under failure and long sessions? |
| Performance | Does it stay inside measured CPU/GPU/memory/network budgets? |
| Maintainability | Can it change without unrelated edits? |
| Testability | Can claims be checked deterministically? |
| Observability | Can failure be detected and diagnosed? |
| Recoverability | Can partial failure return to a valid state? |
| Security/authority | Can untrusted actors create invalid truth? |
| Accessibility | Can target players perceive and operate it? |
| Moddability | Are extension boundaries intentional and safe? |

Not every attribute is critical for every task. The system spec must name the critical subset and measurable thresholds.


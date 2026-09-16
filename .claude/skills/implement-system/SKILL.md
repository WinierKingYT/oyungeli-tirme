---
name: implement-system
description: Implement one approved task under an active implementation lease and stop on scope expansion.
disable-model-invocation: true
---

Implement `$ARGUMENTS` only after confirming a valid active lease.

1. Read the exact task contract, system spec, accepted ADRs, and expected diff.
2. Reconfirm repository reality and cleanly separate pre-existing changes.
3. Report confidence and intended file changes.
4. Implement the smallest coherent change within `allowed_paths`.
5. Run only approved or explicitly confirmed commands.
6. Stop on drift, ambiguity, dependency change, schema change, or scope expansion.
7. Record actual diff, tests, runtime evidence, deviations, and limitations.
8. Hand off for independent review; never self-accept.


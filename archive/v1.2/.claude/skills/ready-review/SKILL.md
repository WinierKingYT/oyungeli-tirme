---
name: ready-review
description: Independently decide whether a proposed system and task are ready for implementation.
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Review `$ARGUMENTS` without repairing it.

Verify repository reality, authority consistency, bounded scope, non-scope, ownership, dependencies, interfaces, lifecycle, multiplayer, persistence, failure cases, performance, observability, acceptance criteria, testability, expected diff, allowed paths, allowed commands, rollback, and stop conditions.

Compute or request the exact task digest with `python scripts/task_digest.py <task-contract>`. Create a separate receipt from `docs/templates/READY-REVIEW-RECEIPT-TEMPLATE.md`; never place the decision only inside the task document.

Return only:

- `READY_FOR_IMPLEMENTATION` with a receipt bound to the unchanged task SHA-256; or
- `FIX_FIRST` with blocking findings; or
- `BLOCKED` with missing evidence.

The reviewer must be independent of the proposed implementation author.


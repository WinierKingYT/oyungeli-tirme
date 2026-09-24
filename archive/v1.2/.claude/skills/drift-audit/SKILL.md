---
name: drift-audit
description: Audit code, assets, configuration, docs, evidence, and lifecycle state for contradictions.
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Audit `$ARGUMENTS` read-only.

Compare documented capabilities, owners, interfaces, commands, dependencies, statuses, test claims, and revisions with repository reality. Report paired evidence for every mismatch.

Classify each finding as `DRIFT`, `STALE`, `MISSING`, or `AUTHORITY_CONFLICT`. Do not repair during audit. Return `CONSISTENT`, `FIX_FIRST`, or `BLOCKED`.


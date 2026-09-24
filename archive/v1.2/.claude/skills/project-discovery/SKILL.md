---
name: project-discovery
description: Establish repository and engine reality before architecture or implementation work begins.
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Investigate `$ARGUMENTS` without modifying production files.

1. Read project status, constitution, current milestone, and accepted ADR index.
2. Detect engine/version, plugins/packages, targets, build/test commands, source modules, asset structure, networking, persistence, CI, and release configuration.
3. Map existing capabilities and canonical owners.
4. Compare documentation claims with repository reality.
5. Record unknowns and a confidence matrix.
6. Produce or update a discovery report; label all unverified claims.
7. Stop with `DRIFT_DETECTED`, `SPIKE_REQUIRED`, or `RESEARCH_COMPLETE`.

Do not authorize implementation.


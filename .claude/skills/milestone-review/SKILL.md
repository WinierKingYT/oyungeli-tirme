---
name: milestone-review
description: Gate a milestone using evidence, integration, risk, defects, performance, and abort criteria.
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Review milestone `$ARGUMENTS` against its exit criteria.

Check system maturity, E2E integration, build/package, target platforms, save migration, multiplayer stability, performance budgets, soak results, playtest outcomes, risk register, defect thresholds, documentation, and abort/replan criteria.

Return exactly `PASS`, `FIX_FIRST`, `REPLAN`, or `BLOCKED`. Dates do not close milestones; evidence does.


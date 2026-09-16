---
name: verify-system
description: Validate an implemented task against acceptance criteria and produce an evidence pack.
disable-model-invocation: true
---

Verify `$ARGUMENTS` against the approved contract.

1. Establish revision, environment, platform, build configuration, and test data.
2. Map every acceptance criterion to evidence.
3. Run applicable build, automated, runtime, multiplayer, persistence, failure-injection, performance, soak, and asset checks.
4. Capture commands, timestamps, outputs, artifacts, seeds, scenarios, and failures.
5. Separate pre-existing failures from introduced regressions.
6. Create an evidence pack using `docs/templates/EVIDENCE-PACK-TEMPLATE.md`.
7. Return `VERIFIED`, `FIX_FIRST`, or `BLOCKED`; do not return final acceptance.


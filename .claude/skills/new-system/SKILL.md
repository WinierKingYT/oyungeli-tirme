---
name: new-system
description: Create a bounded system specification from validated discovery and accepted project authority.
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

For system `$ARGUMENTS`:

1. Verify repository discovery is current.
2. Search for existing and overlapping capabilities.
3. Define problem, outcomes, scope, non-scope, actors, state, ownership, lifecycle, interfaces, events, dependencies, configuration, networking, persistence, observability, performance, failure behavior, migration, and accessibility.
4. Classify risk, rigor, reversibility, and blast radius.
5. Define functional and non-functional acceptance criteria.
6. Define tests, runtime evidence, failure injection, and kill criteria.
7. Record unresolved questions and confidence.
8. Create a `PROPOSED` system spec from `docs/templates/SYSTEM-SPEC-TEMPLATE.md`.

Do not label it ready and do not implement it.


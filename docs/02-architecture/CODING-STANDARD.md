# Coding Standard

Status: `BOOTSTRAP — REPOSITORY CONVENTIONS OVERRIDE AFTER DISCOVERY`

- Match existing language, module, naming, ownership, error, and test conventions.
- Make invariants explicit at boundaries.
- Prefer small cohesive units and clear data flow over generic frameworks.
- Avoid hidden global state, silent catch/fallback, unchecked casts, and ambiguous booleans.
- Bound loops, retries, queues, caches, tick work, and allocations.
- Comments explain why and constraints, not restate code.
- Public behavior changes require tests and documentation.
- Warnings introduced by the change are defects unless explicitly accepted.
- Formatting is mechanical; architecture is reviewed separately.

Exact compiler, formatter, linter, warning, build, and test commands must be filled from repository discovery.


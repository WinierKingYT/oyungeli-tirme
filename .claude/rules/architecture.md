# Architecture rules

- Every mutable domain fact has one canonical owner.
- Derived state is labeled, rebuildable, and never silently promoted to authority.
- Dependencies follow the accepted system map; cross-layer shortcuts require an ADR.
- Prefer explicit contracts and events over direct subsystem reach-through.
- A new abstraction requires a present, demonstrated problem. “May be useful later” is insufficient.
- Search and delete duplication before adding another manager, service, coordinator, registry, factory, helper, or controller.
- Public interface, schema, ownership, or dependency-direction changes require an accepted ADR.
- Circular dependencies, hidden globals, silent fallbacks, and gameplay logic in UI are prohibited.
- High-cost decisions require alternatives, trade-offs, migration cost, and reversibility analysis.


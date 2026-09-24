---
paths:
  - "Source/**/*Network*"
  - "Source/**/*Multiplayer*"
  - "Source/**/*Replication*"
  - "Plugins/**/*Network*"
---

# Multiplayer rules

- Declare server, owning client, and non-owning client responsibilities for every state transition.
- Never trust client-authored economic, inventory, damage, or progression truth without server validation.
- Define late join, reconnect, disconnect cleanup, ownership transfer, relevancy, ordering, duplication, and rollback behavior.
- Test at the required player count and target latency/loss conditions.
- Record state-drift observability and deterministic reproduction inputs.
- Bandwidth and replication-frequency budgets are acceptance criteria, not afterthoughts.


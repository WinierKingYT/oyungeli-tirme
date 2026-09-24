# Debug Scenario Library

| ID | Setup | Purpose | Seed/save/replay | Expected invariant |
|---|---|---|---|---|
| SCENARIO-CARGO-01 | 20 cargo units on deck | physics/interaction scale | TBD | no loss or ownership drift |
| SCENARIO-ENGINE-03 | engine at 95% heat | warning and recovery | TBD | heat owner remains authoritative |
| SCENARIO-NET-05 | client at 250 ms latency | interaction prediction/authority | TBD | no duplicate cargo/economy state |
| SCENARIO-SHIP-08 | storm + damaged engine | chain crisis/softlock | TBD | at least one explicit recovery/abort path |

Scenarios become authoritative only when implemented, versioned, and runnable from a documented command or menu.


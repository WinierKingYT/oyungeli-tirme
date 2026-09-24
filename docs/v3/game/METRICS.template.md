# Gameplay Metrics

> Single source for spatial and timing numbers. Levels, prefabs, and lint tools read these. Change here first, then content.

## Player
| Metric | Value | Notes |
|---|---|---|
| Capsule height / radius | 1.8 m / 0.35 m | |
| Walk / run speed | 3.5 / 6 m/s | |
| Jump height / max gap | 1.1 m / 2.5 m | |
| Step height / max slope | 0.35 m / 40° | |
| Interaction range | 2.0 m | |
| Camera FOV / eye height | 75° / 1.65 m | |

## Traversal sizing rule
| Use | Size as share of max ability |
|---|---|
| Required path (must be easy) | ≤ 70% |
| Optional / challenge | ≤ 95% |
| Impossible (use as barrier) | ≥ 110% |
Example: max gap 2.5 m → required gaps ≤ 1.75 m, challenge ≤ 2.35 m, barriers ≥ 2.75 m.

## Spaces
| Metric | Minimum | Comfortable |
|---|---|---|
| Corridor width (1 player) | 1.2 m | 2.0 m |
| Corridor width (co-op, 4 players) | 2.5 m | 3.5 m |
| Door width / height | 1.0 / 2.1 m | 1.4 / 2.4 m |
| Ceiling height | 2.4 m | 3.0 m |
| Cover height (crouch / stand) | 0.9 / 1.6 m | |

## Timing
| Metric | Value |
|---|---|
| Max time without a new decision | 30 s |
| Input → first visible response | ≤ 100 ms |
| Dead time flagged (nothing happening after input) | > 0.5 s |
| New player understands first goal | ≤ 90 s |
| Rest beat after high intensity | 20–40 s |
| Target level duration | <fill> |

## Readability
| Metric | Value |
|---|---|
| Landmark visible from critical path | every 30–50 m |
| Interactable highlight distance | 6 m |

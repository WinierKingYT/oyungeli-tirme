# Evaluation Task Set

Each task is run twice per setup (baseline: plain Claude + Unity MCP; v3: with skills/workflows). The same `game/IDENTITY.md` is provided to both so the difference measures craft/process, not just context. Outputs are anonymized and scored with `RUBRIC.md`.

Reference game for tasks: the ship game (`examples/ship-game/SHIP-GAME-BASELINE.md`).

## Design tasks
| ID | Prompt | Notes |
|---|---|---|
| EV-SYS-01 | Design the cargo weight and securing system: placing cargo affects ship balance; unsecured cargo can shift in bad weather. | Tests choice, legibility, interaction with weather/engine |
| EV-SYS-02 | Design the engine heat system and how the crew manages it during a voyage. | Tests chore-loop avoidance, co-op roles |
| EV-SYS-03 | Design the island trade economy (buy/sell, stock, prices) for a 3-island route. | Tests sources/sinks, exploit hunt |
| EV-SYS-04 | Change request: radio failure should make navigation harder but never block progress. | Tests change to existing systems, failure legibility |

## Level tasks (F3)
| ID | Prompt |
|---|---|
| EV-LVL-01 | Blockout the first port: moor, market, load cargo, depart. Must teach cargo placement. |
| EV-LVL-02 | Design a night approach to an island guided by a lighthouse. |

## Implementation tasks
| ID | Prompt |
|---|---|
| EV-IMP-01 | Implement the rules of EV-SYS-01's minimum version in Unity with tests. |
| EV-IMP-02 | Add a debug view for engine heat state. |

## Procedure
1. Fresh session per run; same model; same IDENTITY. Baseline session has no v3 skills/agents loaded (run from a copy without `.claude/skills` v3 entries).
2. Randomly assign which setup is `A` and which is `B` per task (coin flip); write the mapping to `evals/runs/<date>/KEY.md` and do not open it until scoring is finished.
3. Save outputs to `evals/runs/<date>/<task>/A.md` and `B.md` (screenshots in the same folder for level tasks). Strip any mention of skills, agents, or workflow names from outputs before scoring.
4. Score with the `eval-scorer` agent (fresh context per task) and, independently, by the owner using `RUBRIC.md`.
5. Open `KEY.md`, fill `evals/RESULTS.md` from `RESULTS.template.md`, and record the verdict.
6. If owner and scorer disagree by > 1 point on a criterion, note it; repeated disagreement means the rubric wording needs fixing.

## Baseline first
Run the baseline (plain Claude + Unity MCP) once before any v3 skill is used in anger. Every later run compares against it.

# SYS-<ID>: <Name>

Status: `IDEA | DESIGNED | PROTOTYPED | TUNED | SHIPPED` · Owner: <name> · Pillars served: <P1, P3>

## Purpose
<!-- Why this system exists; what player problem or desire it answers. -->

## Player experience
<!-- What the player feels and decides. One concrete moment described in play. -->

## Core loop
<!-- Action → feedback → reward → new decision. Diagram or 3–6 steps. -->

## Inputs / outputs
| Consumes | Produces | From / to system |
|---|---|---|

## Meaningful choices
<!-- Decisions with trade-offs. If there is one obviously best option, it is not a choice. -->

## Formulas
<!-- Every formula with a variable table; no prose-only formulas. -->
`tilt_deg = clamp(k_tilt * (M_right - M_left) / M_total, -max_tilt, max_tilt)`
| Variable | Meaning | Unit | Source (config field) |
|---|---|---|---|

## Tuning parameters (live in ScriptableObjects)
| Parameter | Default | Range | Effect when raised |
|---|---|---|---|

## Edge cases (each with an exact resolution)
| Situation | Resolution |
|---|---|
| <e.g. two players place cargo on the same slot in the same frame> | <e.g. server order wins; second placement is rejected with a sound + outline flash> |

## Failure and ignore states
<!-- What happens when the player ignores, abuses, or fails at this system; how they notice and recover. -->

## Acceptance criteria (observable)
<!-- Each has a same-layer witness: test name, screenshot moment, or playtest question. -->
| # | Criterion | Verified by |
|---|---|---|

## Known risks / exploits

## Open questions

## Decisions
<!-- Link to memory/DECISIONS.md entries. -->

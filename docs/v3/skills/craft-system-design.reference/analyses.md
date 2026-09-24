# System design — analysis formats and anti-patterns

## Contents
- Interaction matrix · Resource flow · Decision inventory · Exploit hunt · Boredom · Balance · Scope · Twist · Anti-patterns · Balance search

## Interaction matrix
| This system → | System A | System B | System C |
|---|---|---|---|
| affects | how | how | — |
| is affected by | how | — | how |
Empty rows = isolated system: justify or redesign.

## Resource flow
| Resource | Sources (+rate) | Sinks (−rate) | Cap | At 0 | At cap |
|---|---|---|---|---|---|

## Decision inventory
| Decision | Options | Trade-off | Info available | Consequence | Dominant option? |
|---|---|---|---|---|---|

## Exploit hunt
| Player type | Exploit | Effect | Fix |
|---|---|---|---|
| min-maxer | | | |
| griefer (co-op) | | | |
| lazy player | | | |

## Boredom check
Where it repeats, after how many repetitions, and what varies (context, combination, escalation).

## Balance (numbers only from config assets or simulation output)
- Sources vs. sinks per session; inflation or starvation trend
- Dominant options on every axis
- Progression dead zones and power spikes
- Degenerate strategies: cheapest repeated action with the best outcome
If data is missing: `NOT ASSESSED — NO DATA` + what the prototype must produce.

## Scope
| Element | ADD / KEEP / DEFER / CUT | Why |
|---|---|---|

## Twist
One sentence: "the game where …". None → state it as a design risk.

## Anti-patterns
Numbers without a described moment · chore loops (upkeep with no decision) · hidden punishment · false choice · feature soup · unbounded snowball · opaque simulation · tuning values hard-coded in code.

## Balance search (when a simulation exists)
1. Write the target in the card as a measurable function (e.g. "net profit per voyage 80–120; bankruptcy rate < 5%; no cargo type > 40% of profit").
2. Run the pure C# rules N times per parameter set (EditMode simulation test or small runner).
3. Sweep the most influential 2–4 parameters (grid or random search first); allocate more runs to promising sets.
4. Report the best sets, their metric values, and the trade-offs between them; the owner picks. Several balanced sets usually exist.
5. For turn-based or text-like decisions, an LLM player can estimate relative difficulty between variants; do not treat it as a measure of fun.

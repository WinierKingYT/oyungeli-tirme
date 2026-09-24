# Design Quality Rubric

Score each criterion 1–5. Scorers see outputs anonymized (A/B), not which setup produced them.

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| **Pillar fit** | Generic; could be in any game | Fits the game but touches pillars loosely | Clearly amplifies named pillars; respects non-goals |
| **Meaningful choice** | No decisions or one dominant option | Some real trade-offs, a few obvious answers | Several decisions with clear trade-offs, info, and consequences |
| **Clarity / readability** | Player could not predict or understand outcomes | Mostly readable, some opaque parts | Player can predict, read feedback, and learn from failure |
| **Feasibility** | Vague or unbuildable; no tuning plan | Buildable; some unknowns unaddressed | Minimum version defined; tunables listed; risks with tests |
| **Novelty** | Stock genre solution | Familiar with a twist | Fresh interaction that fits the game |
| **Systemic depth** | Isolated rule set | Connects to 1–2 systems | Interacts with several systems to create emergent stories |

For implementation tasks add (judged on the running build, not the code alone):

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| **Build health** | Does not compile or errors at runtime | Runs with console errors or unstable behavior | Compiles, tests pass, console clean during the scenario |
| **Visual usability** | Screenshots show broken, unreadable, or missing elements | Readable with noticeable problems | Screenshots clearly show the intended state; nothing obscured |
| **Intent alignment** | Behavior does not match the card/prompt | Partly matches; key parts missing | Every acceptance criterion observably met |
| **Code structure** | Logic in MonoBehaviours, magic numbers | Partly separated | Script roles respected; pure logic + adapter + config; tested |

For level tasks add:

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| **Navigation clarity** | Screenshots do not show where to go | Main path readable, decision points ambiguous | From every review point the intended direction is the most salient |
| **Pacing** | Flat or random intensity | Some rest beats, uneven | Card curve realized; peaks followed by dips |
| **Metrics compliance** | Violations on the critical path | Minor violations off-path | Lint and critical path clean |

For build/playtest tasks use the playability score from `/playtest` (6 dimensions, /12) and, for feel tasks, the `/14` rubric from `craft-game-feel`.

## Skill trigger tests
Each skill also has a small trigger set in `evals/triggers/<skill>.md`:
- 3 prompts that **should** load it,
- 3 decoy prompts that **must not** load it,
- 1 action case proven by a tool call in the transcript (e.g. `/unity-test` actually invoked the test tool), not by the wording of the reply.
Run after any change to a skill's description.

Report: per-criterion mean, total mean, and notable comments. A change "improves quality" when the v3 mean exceeds the baseline mean by ≥ 0.5 across the task set without any criterion dropping by > 0.5.

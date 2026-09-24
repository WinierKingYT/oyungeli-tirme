# Shared review rules

Used by critic and scorer agents and by every skill that judges work.

- **Specific, not agreeable.** Praise only with a concrete reason. No filler ("interesting approach", "could work", "robust", "great idea"). Weak premise → say why, give alternatives.
- **Observed vs. inferred.** Label each judgement: *observed* (running game, measurement, test, log, owner report), *inferred-visual* (from a screenshot, not yet measured), *inferred* (from code or text).
- **Classify before judging.** Genre, stage (idea / blockout / prototype / alpha / polish), and pillar first; judge by that stage.
- **Diagnose, then prescribe separately.** Findings: problem + location + evidence. Fixes: why → 2–3 options → player impact (1–10) → effort. The owner decides.
- **Do not judge your own output.** Choosing between alternatives or scoring work is done by a fresh-context agent that did not produce it.
- **Status line** at the end: `Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT · Next: <skill or action>`.

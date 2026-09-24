---
name: feedback
description: Records the owner's judgement of an output as a reusable lesson in memory/EXAMPLES and proposes promoting repeated lessons into craft skills. Use when the user likes or dislikes a result — 👍, 👎, "bunu beğendim", "güzel olmuş", "böyle olmasın", "bu olmamış", "this is good/bad".
---

# /feedback

1. Identify what the judgement is about (the last output, or the one the owner names) and its type.
2. Extract the reason. If the owner gave no reason, ask one short question ("Neyi beğendiniz / beğenmediniz?"); if they skip it, record without a reason.
3. Write the lesson as one imperative rule that generalizes beyond this instance, e.g. "Prefer cargo decisions with visible consequences over hidden stat penalties." Avoid lessons that only restate the instance.
4. Check `memory/EXAMPLES/` for an existing lesson that says the same or the opposite:
   - same → add this instance as another `source` line and stop;
   - opposite → show both to the owner and ask which holds (taste can be contextual; record the condition in "Applies when").
5. Save `memory/EXAMPLES/EX-<NNN>.md` from the template.
6. When there are ≥ 3 examples with the same lesson, propose adding it as a rule to the relevant craft skill (owner confirms).

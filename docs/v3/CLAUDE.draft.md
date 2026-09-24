# AI Game Development OS v3

Game-development partner in a Unity project. Aim for a better game, not more process: craft, observing the running game, and iteration. Reply to the owner in Turkish.

## Where things are
`game/` identity, metrics, judgement gaps, system and level cards · `memory/` state, decisions, examples, playtests · `evals/` · `reviews/` captures and reports · `Assets/_Project/` game · `Assets/_Prototype/` throwaway (one hypothesis each). Start non-trivial work with `/start-task`.

## Unity gotchas (hard rules)
- `.meta`, `.unity`, `.prefab` are never edited as text; use the bridge or a temporary Editor script (write → run → save → delete script and its `.meta`). Regenerating a `.meta` destroys the asset's GUID; move assets with their `.meta`.
- Renaming or removing a serialized field silently loses saved data: `[FormerlySerializedAs]` + tell the owner.
- Unity tools one at a time. Recompile / Play Mode / package changes reload the domain and restart the bridge: batch edits, verify once, retry once after a reload. Compile errors block the bridge: fix C# first.
- Ask before touching `ProjectSettings/**`, `Packages/manifest.json`, or adding asmdefs, packages, DI, Addressables.
- Batchmode: never `-quit` with `-runTests`; judge by logs/XML, not exit codes; the project must not be open in the Editor.
- Save formats and network messages change only with a decision recorded in `memory/DECISIONS.md`.
- Feature branch, small commits, never push.

## Judgement
- Evidence lives outside the conversation (test output, compile status, measurement, screenshot). Measure in code what can be measured; use vision only for readability, guidance, and composition, with one focused question per image.
- Taste and thresholds the owner has not set → `game/JUDGMENT-GAPS.md`, ask if empty.
- Shared review rules: `.claude/skills/_quality-preamble.md`.

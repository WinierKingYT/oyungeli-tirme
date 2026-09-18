---
paths:
  - "Assets/**/*"
  - "Packages/manifest.json"
  - "Packages/packages-lock.json"
  - "ProjectSettings/**/*"
---

# Unity engine profile (PROPOSED, not repository-verified)

- Treat Unity version, render pipeline, installed packages, scripting backend, target platforms, networking stack, and save strategy as repository facts to discover.
- Do not create a new subsystem when an accepted owner already exists.
- Avoid unbounded per-frame callbacks, systems, or jobs; prefer events, timers, or bounded scheduled work. In GameObject-based code, keep per-frame allocations, `GetComponent`, and `Find*` calls out of hot paths.
- Keep gameplay rules out of UI and presentation-only components.
- ScriptableObjects or accepted project configuration own tunable gameplay data; avoid magic constants.
- Prefer the editor or an approved Unity CLI path over text edits to `.unity`, `.prefab`, `.asset`, and `.meta` files. Never move, rename, or delete an asset without its `.meta`, because GUID references break.
- Never commit generated folders (`Library/`, `Temp/`, `Logs/`, `obj/`, `UserSettings/`) or conventional build output folders such as `Builds/`.
- Renaming a serialized field loses data; use `FormerlySerializedAs` and record the migration.
- Respect assembly-definition dependency direction; circular asmdef references are prohibited.
- Replicate authoritative state, not cosmetic consequences. Define ownership, RPC direction, validation, and late-join behavior for the chosen networking stack.
- Compilation success does not prove Edit Mode or Play Mode tests, multiplayer, player builds, or target-platform behavior.

---
paths:
  - "Source/**/*.{h,cpp,cs}"
  - "Config/**/*.ini"
  - "Plugins/**/*"
  - "Content/**/*"
---

# Unreal Engine profile

- Treat Unreal version, enabled plugins, target platforms, build targets, networking model, and save strategy as repository facts to discover.
- Do not create a new subsystem when an accepted owner already exists.
- Avoid unbounded `Tick`; prefer events, timers, or bounded scheduled work.
- Replicate authoritative state, not cosmetic consequences. Define ownership, RPC direction, validation, relevancy, dormancy, and late-join behavior.
- Keep gameplay rules out of widgets and presentation-only actors.
- DataAssets or accepted project configuration own tunable gameplay data; avoid magic constants.
- Asset paths, redirectors, Blueprint parents, interfaces, collision profiles, and cooking implications require validation.
- Never edit binary `.uasset` or `.umap` files through text tools.
- Build success does not prove editor runtime, PIE multiplayer, packaging, or target-platform behavior.


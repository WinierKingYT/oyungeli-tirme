---
paths:
  - "Content/**/*"
  - "Assets/**/*"
  - "Art/**/*"
---

# Asset production rules

- Validate scale, orientation, naming, pivots, transforms, topology, UVs, materials, textures, collision, LODs, skeleton, animations, compression, and platform budgets.
- Reject missing references, stale skeletons, excessive materials, unsupported texture sizes, and absent collision where required.
- Preserve source provenance and license metadata.
- Generated assets are candidates until visually and mechanically reviewed in-engine.
- A screenshot is not proof of collision, animation deformation, LOD transition, memory cost, or packaged-build behavior.
- Changes to a frozen skeleton, socket contract, master material, collision profile, or naming convention require change control.


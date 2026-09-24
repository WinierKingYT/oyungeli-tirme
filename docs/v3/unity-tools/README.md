# Unity review tools (F3)

Status: `DRAFT — not compiled`. Written without a Unity project; first compile and test happen after the F1 setup.

| Tool | File | Menu | Output |
|---|---|---|---|
| Review marker | `Runtime/ReviewPoint.cs` | — (component) | Gizmo in scene |
| capture_review_set | `Editor/ReviewCapture.cs` | Tools/Review/Capture Review Set | `reviews/<date>/<scene>/*.png` + `index.json` |
| lint_scene | `Editor/SceneLint.cs` | Tools/Review/Lint Scene | `reviews/<date>/<scene>/lint.json` |
| measure_critical_path | `Editor/CriticalPathProbe.cs` | Tools/Review/Measure Critical Path | `reviews/<date>/<scene>/path.json` |
| compare_images | `Editor/ImageDiff.cs` | — (`ImageDiff.Compare(before, after)`) | `<after>_diff.png` + JSON: changed share, bounding box |
| validate_layout / apply_layout | `Editor/LayoutPlan.cs` | — (`LayoutPlan.Validate(path)`, `LayoutPlan.Apply(path)`) | "OK" or one line per metric violation; applies primitives under `_Env/Blockout` in one undo step |

Why these two: vision models are weak at before/after comparison and fine placement, so change detection and metric checks are done in code; vision only describes the region the diff points to. Blockouts follow plan → validate → apply so metric errors are caught before the scene changes.

## Bridge independence
The tools are plain menu items + static methods on purpose, so they work with any bridge (official CLI/MCP by running C# or `-executeMethod`, IvanMurzak by wrapping with `[AiTool]`, CoplayDev custom tools). See `docs/research/11-unity-mcp-servers.md`.

## How the agent calls them
Unity MCP servers can execute a menu item or run C# in the Editor. Use either:
- execute menu item `Tools/Review/...`, then read the console line for the result path; or
- invoke the static method (`Game.EditorTools.ReviewCapture.CaptureActiveScene()` etc.) and read the returned string.
Then read the PNGs / JSON from the output folder. If the chosen MCP supports custom tool registration, wrap these three methods as named tools.

## Assemblies
- `ReviewPoint` → runtime assembly `Game.Tools` (no dependencies).
- Editor tools → `Game.Editor` (references `Game.Tools`; Editor platform only).
- `CriticalPathProbe` needs the AI Navigation package and a baked NavMesh.

## First-run test plan (after F1)
1. Empty scene with a plane + cube, `ReviewPoint` Start and Goal: capture produces overview + 2 images; index.json lists them.
2. Add a cube without collider under `_Env`, a missing script, a root named `Stuff`: lint reports each once.
3. Bake NavMesh; path reports reachable and a plausible length; put Goal on an unreachable platform: reports `NOT reachable`.
4. Capture the same view twice with no change → `compare_images` reports ~0% changed; move one cube → the bounding box covers it.
5. `layout.json` with a required 2.2 m gap and a 1.0 m corridor → Validate lists both; fixed plan → "OK"; Apply creates the elements and one Ctrl+Z removes them.
6. Check render pipeline: with URP, confirm `Camera.Render()` into a RenderTexture produces non-black images; if not, switch to `RenderPipeline.SubmitRenderRequest` (Unity 6) — known risk.

## Known limitations
- Critical-path ordering uses straight-line progress, so heavily winding levels may order intermediate points wrong; label points in order if needed (future: explicit order field).
- Lint "walkable" check treats everything under `_Env` as walkable geometry.
- LayoutPlan only builds cubes and checks a few metrics (gaps, corridor width, ceiling, awkward platform heights); ramps and non-box shapes come later.
- Walk speed and layout limits are duplicated from METRICS.md; keep them in sync (future: read from a Metrics ScriptableObject).

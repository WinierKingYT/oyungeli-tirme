# Unity Repository Hygiene Standard

Status: `PROPOSED`. General Unity practice, not verified against the installed Unity version or this repository. Every item is checked during `UNITY-SETUP-001`; a failed check changes this document, not the other way round.

## Layout

- The Unity project root is the repository root (`Assets/`, `Packages/`, `ProjectSettings/` at the top level), because the governance package must be installed at the Git root and `.claude/rules/unity.md` matches `Assets/**`.
- Governance and documentation folders (`.claude/`, `.ai-governance/`, `docs/`, `scripts/`, `schemas/`, `tests/`) stay outside `Assets/`. Unity only imports `Assets/` and `Packages/`.
- Unity does not create a project in a non-empty folder. Create it in a temporary folder, then move `Assets/`, `Packages/`, and `ProjectSettings/` into the repository root.

## Track and ignore

- Track: `Assets/` (including every `.meta`), `Packages/manifest.json`, `Packages/packages-lock.json`, `ProjectSettings/` (including `ProjectVersion.txt`).
- Ignore (proposed `.gitignore` entries): `/[Ll]ibrary/`, `/[Tt]emp/`, `/[Oo]bj/`, `/[Bb]uild/`, `/[Bb]uilds/`, `/[Ll]ogs/`, `/[Uu]ser[Ss]ettings/`, `/[Mm]emoryCaptures/`, generated IDE files (`*.csproj`, `*.sln`, `*.suo`, `*.user`, `.vs/`), and platform build outputs (`*.apk`, `*.aab`, `*.unitypackage`).
- Never ignore `.meta` files; a missing `.meta` breaks GUID references.

## Editor settings to verify

- Asset Serialization: `Force Text`, so scenes and prefabs diff as text.
- Version Control Mode: `Visible Meta Files`.
- Check both in `ProjectSettings/EditorSettings.asset` after project creation and record the exact keys and values found.

## Version pin

`ProjectSettings/ProjectVersion.txt` records the editor version. Everyone uses that exact version. Changing it needs an accepted ADR (high-cost, hard to reverse).

## Line endings

This machine has system-wide `core.autocrlf=true`. Whether to add a `.gitattributes` for Unity YAML files and `.meta` is `OPEN`: the wrong choice creates noisy diffs. Decide with a spike on the real project before the first large commit.

## Large binaries (Git LFS)

Decide the LFS patterns (textures, audio, models, video) before the first binary asset is committed. Adding LFS afterwards means rewriting history, which agents may not do without explicit authorization. Status: `OPEN`.

## Assembly definitions and tests

- One-way dependencies. Production code under `Assets/Game/**`; the prototype lane under `Assets/_Prototype/**` in its own assembly definition that nothing else references (`PROTOTYPE-LANE.md`).
- Tests use Unity Test Framework: an Edit Mode assembly and a Play Mode assembly. Whether Unity's batch-mode test runner can be invoked under lease and hook command restrictions is a spike; do not assume it works.

## Open decisions (owner input or ADR-003)

Unity version, render pipeline (Built-in, URP, HDRP), 2D or 3D, input system, networking stack (if multiplayer), LFS patterns, line-ending policy.

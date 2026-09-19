# EVID-TASK-UNITY-RULES-001-R1 — Evidence Pack

Status: `DRAFT` (submitted for independent acceptance review; not accepted)

## Identity

- Task/system: `TASK-UNITY-RULES-001` / system `UNSET` (see the contract's `system_id` note)
- Commit/revision: `3d818775260a050021d31cf910b96c245366ac5a` (`chore: add proposed Unity engine rule profile (TASK-UNITY-RULES-001)`, branch `main`)
- Build/configuration/platform: no build applies (one static Markdown rule file); Windows 11 Pro, Python 3.13.7, Git for Windows with system `core.autocrlf=true`
- Date/operator: 2026-09-18; the human operator ran the lease, seal, commit, and validator commands in their own PowerShell terminal; the drafting agent wrote the implementation file under the lease and this pack

## Repository-bound implementation

- Base Git HEAD: `ae095ac7ce99810ee9670947545299742428b913` (printed by `activate_lease.py`)
- Implementation seal path: `.ai-governance/implementation-seals/TASK-UNITY-RULES-001-3ac61d20ca61-ae095ac7ce99.json` (gitignored, local file)
- Implementation seal SHA-256: `72b6e9beef68504e7c8a300ac00bc862d3573b4597a472bdf1d3dda83105f058`
- Implementation diff SHA-256: `1b33f43e56225f9a41b883941295c8027dcfda75210332d7087ddcd8b4db8f24`
- Changed paths verified against lease: `seal_implementation.py` rejects any changed path outside `allowed_paths`; it sealed successfully. After implementation `git status --short` showed exactly `?? .claude/rules/unity.md`.
- Task contract SHA-256 bound by the READY receipt: `3ac61d20ca614b9bd3f655604e6eab84e463ec76df5e368538726eb0d509e236`

## Manifest and provenance

- Implemented file: `.claude/rules/unity.md`, SHA-256 `8f9e4079b673840123f8fdfaa6f44e780180e2669e1555bd2967f293fcc1807e` (`python scripts/artifact_digest.py`, worktree bytes, LF endings). Git may store or check it out with CRLF (`core.autocrlf=true`); the digest above is of the worktree bytes.
- The content was copied from the contract's "Proposed file content" block. The author-side inspection found 21 lines, no CR characters, and four `paths` entries (Grep counts on 2026-09-18).
- The READY receipt is `docs/05-production/tasks/READY-TASK-UNITY-RULES-001.md`.

## Actual diff vs expected diff

| Kind | Expected | Actual |
|---|---|---|
| New files | `.claude/rules/unity.md` | `.claude/rules/unity.md` (`1 file changed, 21 insertions(+)`, `create mode 100644`) |
| Modified files | None | None in the implementation commit |
| Removed files | 0 | 0 |
| Dependencies | None | None |
| Schema/public contract | None | None |

## Acceptance matrix

| AC | Method | Evidence artifact | Result | Notes |
|---|---|---|---|---|
| AC-01 | Compare the file to the contract block; record SHA-256 | Implemented file and its SHA-256 above | Author-verified; independent comparison pending | The recorded SHA-256 ties the file to the seal; it is not an independent check |
| AC-02 | Manual inspection | File heading `Unity engine profile (PROPOSED, not repository-verified)` and first bullet | Author-verified; independent inspection pending | No Unity version, pipeline, package, or networking stack is asserted as chosen |
| AC-03 | `git status --short` and commit stat | Command outputs above | PASS | `unreal.md` is not in the commit |
| AC-04 | `python scripts/validate_os.py` | Output below | PASS in a clean copy; see deviation | 169 checks, `RESULT: PASS`, 126 Markdown files |
| AC-05 | `python scripts/doctor.py` | Output below | PASS in a clean copy; see deviation | `RESULT: PASS` |
| AC-06 | Manual inspection of the first lines | Grep count of `^  - "` = 4 | Author-verified; independent inspection pending | One `---` delimited block |

## Commands and machine-readable outputs

Run by the human on 2026-09-18 in a temporary copy of the repository made with `robocopy . $t /E /XD __pycache__ implementation-seals /XF *.pyc implementation-lease.json`, run before the commit while `unity.md` was present but untracked:

```
python scripts/doctor.py
  Python: 3.13.7
  Claude Code: C:\Users\faruk\.local\bin\claude.EXE
  Git: C:\Program Files\Git\cmd\git.EXE
  RESULT: PASS
python scripts/validate_os.py
  Checks: 169
  Markdown files: 126
  Agents: 8
  Skills: 9
  RESULT: PASS
```

Other commands: `python scripts/activate_lease.py ... --hours 1` (lease until `2026-09-18T19:07:21.935517Z`), `python scripts/seal_implementation.py` (`SEALED: TASK-UNITY-RULES-001`), `git commit` (`3d81877`).

## Runtime, multiplayer, persistence, performance, failure, and soak evidence

Not applicable to a static, dormant Markdown rule file. No runtime, multiplayer, persistence, performance, failure-injection, or soak evidence exists or is claimed.

## Pre-existing failures, deviations, limitations, and residual risk

- **Deviation (AC-04, AC-05):** `scripts/validate_os.py:115-117` fails whenever `.ai-governance/implementation-lease.json` or any file in `.ai-governance/implementation-seals/` exists on disk, so neither validator can run in place after activation. Both ran in a copy without those artifacts. The copy was otherwise the working tree, including the untracked `schemas/` and `TASK-STATE-TRANSITION-001.md`. Recorded as `DEBT-006`.
- **Limitation:** nothing tests that the rule loads for Unity paths, because no Unity path exists. AC-04 and AC-05 are regression guards only; validators never reference `.claude/rules`.
- **Limitation:** the validator run has no recorded time of day; only the date is known.
- **Limitation:** the rule content comes from general Unity practice, not from this repository, and is unverified (`PROPOSED`).
- **Limitation:** author, reviewers, and receipt transcriber share the same underlying model, so independence is procedural, not cryptographic.
- **Known drift, out of scope:** other Unreal remnants are logged as `DEBT-005`.
- Residual risk: low. The file only affects agent behavior when a matching Unity path is edited, and it is reversible by deleting the file.

## Independent review disposition

The final disposition lives in a separate acceptance receipt containing this pack's deterministic SHA-256 and the exact implementation revision.

# ADR-001 — Adopt the V2.0 Product and Threat Specification direction (controller-based architecture)

Status: `ACCEPTED`

Date: 2026-09-16

## Context and forces

The v1.2 baseline of AI Game Development OS was verified in this session: `python scripts/validate_os.py` passes 169 mechanical/adversarial checks (114 markdown files, 8 agents, 9 skills), matching the packaged claims. The verification also surfaced 13 findings, the most severe being that the repository was not a Git repository at all (since remediated — see Git bring-up, commit `c780f6b`), and that `.claude/hooks/govern_shell.py`'s regex-based shell gate can be evaded by nested-interpreter payloads (e.g. `perl -e "system('git push ...')"`), a limitation already disclosed in `docs/00-project/SECURITY-THREAT-MODEL.md:22` but not yet architecturally closed.

An external development brief ("AI Game Development OS 2.0 — Development Brief and Execution Contract for Claude Sonnet") proposed evolving v1.2's in-process, repository-local hook model into a v2.0 architecture where a **trusted external controller** — running outside the governed agent's own shell — mediates authority, sandboxing, evidence, and merge decisions. This directly addresses the shell-gate class of limitation, since the enforcement boundary moves from "inside the same process being governed" to "a separate process the agent cannot influence."

A V2-01 product-and-threat specification was drafted, independently reviewed by three separate fresh-context reviewers (architecture/correctness, adversarial/evidence-coverage, documentation-consistency), all of which returned `FIX_FIRST`. The specification was revised (rev.2) to address all nine findings from that round: a fabricated citation was removed, the proposed lifecycle was withdrawn in favor of reusing the existing `docs/08-process/SYSTEM-LIFECYCLE.md` unchanged, the rigor-policy table was reconciled against the real `docs/00-project/RIGOR-RISK-MODEL.md` instead of an unreconciled external baseline, the CI/sandbox incompatibility (Windows Sandbox not available on CI runners) was resolved by scoping the sandbox mandate differently for local vs. CI execution, a bootstrap-gap section was added, an internal WSL2 contradiction was removed, the "provider-neutral" claim was corrected to describe only the MVP's internal interface (not its actual GitHub-only behavior), concurrency/race coverage was added to the failure model, and the usability-budget deferral was given an explicit owner, trigger, and fallback rule.

## Decision drivers

- PR1–PR7 (product requirements): no agent self-grants authority; no acceptance without immutable evidence; every state transition auditable; reviewer technically separated from implementation; engine claims require engine evidence; usability budget must be measured, not assumed; project must remain exportable without lock-in.
- The project's own standing rules (`AGENTS.md`, `.claude/rules/architecture.md`, `docs/00-project/AUTHORITY-MODEL.md`) require that authority conflicts and schema/lifecycle changes never be resolved silently — this ADR exists to make that resolution explicit and inspectable rather than implicit.

## Options considered

| Option | Benefits | Costs/risks | Migration | Reversibility |
|---|---|---|---|---|
| Keep v1.2 in-process hook model unchanged | No new work; already validated (169 checks pass) | Shell-gate bypass class (nested interpreters) remains architecturally open; no external controller means agent's own process is always in the trust boundary | None needed | N/A — status quo |
| Adopt V2.0 controller-based architecture (this ADR) | Moves enforcement outside the governed process; adds capability-based (not exact-name) MCP mediation; adds hash-chained evidence ledger | Large undertaking (external brief estimates 4–6 months full-time); introduces new unresolved decisions (sandbox mechanism, credential broker) that must be spiked before implementation | Incremental — v1.2 remains the accepted baseline until v2.0 phases individually clear their own gates | Moderate — no code has been written yet; this ADR only accepts the direction and its already-resolved sub-decisions, not an implementation |

## Decision

Adopt the V2.0 product-and-threat specification (rev.2) as the accepted direction for future work, with the following sub-decisions **already resolved and binding**:

- **D1** — First supported host environment: Windows native.
- **D2** — First engine adapter: none; controller MVP is built before any engine integration.
- **D3** — Execution model: local + CI.
- **D4** — Sandbox strength: rigor tier R2 and above require OS-level isolation, mandatory for local execution once a mechanism is selected via spike; for CI execution, the CI provider's own per-job runner isolation is accepted as an interim substitute pending its own verification.
- **D6** — Git provider: GitHub first; the controller's merge-gate *interface* is designed abstractly, but its MVP *behavior* is GitHub-specific, not provider-neutral.
- **D7** — Remote MCP tools: disabled for the entire initial pilot (matches v1.2's already-empty `allow_without_lease`/`allow_with_lease` lists).
- **D9** — Evidence retention: follows the existing local/git-ignored precedent (`.ai-governance/audit.log`, `implementation-lease.json`) until a written retention policy is adopted separately.

The following remain explicitly **open and blocking** further phases, per `AGENTS.md`'s uncertainty protocol — this ADR does not resolve them:

- **D5** — Claude Code / Sonnet version pinning policy (`ASSUMPTION_REQUIRES_APPROVAL` at each phase start rather than fixed now).
- **D8** — Key custody / reviewer identity policy (proposed: SSH-signed receipts by default from R1 up, not just R4 — usability cost not yet evidenced).
- **D10** — Measurable usability budget (`SPIKE_REQUIRED`; owner = project owner; trigger = completion of the V2-09 pilot batch; fallback = reopening the D4 sandbox mandate if overhead proves unacceptable).
- The Windows sandbox mechanism itself (Windows Sandbox vs. Hyper-V isolated containers) — `SPIKE_REQUIRED` before the Worktree/Sandbox Manager phase begins.

No lifecycle vocabulary change is accepted by this ADR: `docs/08-process/SYSTEM-LIFECYCLE.md`'s nine states remain authoritative and unchanged. A single new terminal state (`MERGED`, between `ACCEPTED` and `FROZEN`) was proposed in the V2-01 draft but is **not** accepted here — it requires its own dedicated ADR before `SYSTEM-LIFECYCLE.md` is edited, per `.claude/rules/architecture.md`'s schema-change rule.

Similarly, no change to `docs/00-project/RIGOR-RISK-MODEL.md` is accepted by this ADR. The R2 OS-isolation requirement (D4) is recorded here as a **V2.0 addendum layered on top of** the existing rigor model, not a replacement of it, and itself requires its own ADR before `RIGOR-RISK-MODEL.md` is edited.

## Consequences

- v1.2 remains the accepted, unmodified operational baseline. This ADR authorizes further specification and spike work toward v2.0; it does **not** authorize any v2.0 implementation. Per the source brief's own rule and this session's standing instruction, "do not begin v2.0 implementation merely because this document exists."
- Two known items now block the next phase (V2-02, contracts/schemas) from starting cleanly: `DEBT-001`/`RISK-006` (doctor.py's non-ASCII path comparison bug) and the two still-open sandbox/usability spikes above.
- Future R2+ work under this repository's own v1.2 lease mechanism is unaffected by this ADR; it continues to operate exactly as validated (169 checks passing) until superseded by an implemented v2.0 phase.

## Validation and revisit trigger

Revisit this ADR if: the V2-09 pilot batch (5×R1/R2 + 3×R3 + 2×R4 tasks) shows unacceptable overhead (see D10 fallback); the sandbox-mechanism spike finds none of the three Windows-native candidates viable; or repository discovery (still `NOT_STARTED` per `docs/00-project/PROJECT-STATUS.md`) reveals a different engine/platform reality than assumed here.

## Supersedes / superseded by

Supersedes: none. Superseded by: none yet.

## Independent review record

- V2-01 rev.1 reviewed independently by three fresh-context agents (`code-reviewer`, `qa-reviewer`, `documentation-auditor`), 2026-09-16 — unanimous `FIX_FIRST`, nine findings, all addressed in rev.2 (see Context above).
- rev.2 itself did not go through a second automated independent-reviewer round. Final acceptance of this ADR is the **project owner's own decision**, given directly in conversation on 2026-09-16 — satisfying `AGENTS.md`'s rule that the task author (this agent, who drafted V2-01) cannot be its own approval authority, since the approving party here is a different, human principal.

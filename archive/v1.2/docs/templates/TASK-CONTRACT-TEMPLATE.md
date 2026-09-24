---
task_id: TASK-SYSTEM-000
status: DRAFT
authored_by: UNSET
approved_by: UNSET
ready_review_receipt: UNSET
rigor: R2
approval_mode: hash
system_id: SYS-SYSTEM-000
allowed_paths:
  - Source/Project/System/**
  - Tests/System/**
allowed_commands:
  - git diff *
  - UnrealEditor-Cmd *
---

# Task Contract — TASK-SYSTEM-000

## Problem and outcome

## Authority inputs

## In scope

## Explicit non-scope

## Repository reality and relevant existing capability

## Expected diff

| Kind | Expected |
|---|---|
| New files | |
| Modified files | |
| Removed files | 0 unless explicitly approved |
| Dependencies | None unless explicitly approved |
| Schema/public contract | None unless explicitly approved |

## Blast radius and reversibility

## Acceptance criteria

| ID | Criterion | Verification | Required evidence |
|---|---|---|---|
| AC-01 | | | |

## Test and runtime plan

## Stop conditions

- Scope expansion.
- Documentation/code drift invalidates the contract.
- Material confidence becomes LOW.
- Required dependency/schema/public interface change is discovered.
- Lease is absent, expired, or invalid.

## Rollback

## Independent ready review

The independent reviewer creates a separate immutable receipt from `READY-REVIEW-RECEIPT-TEMPLATE.md`. The receipt binds its disposition to the final SHA-256 of this task contract. After that digest is recorded, changing this task invalidates the review.

Use `approval_mode: hash` for R0–R3. R4 requires `approval_mode: ssh-signature` and a trusted reviewer signature.

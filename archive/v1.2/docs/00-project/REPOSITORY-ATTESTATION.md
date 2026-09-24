# Repository-Bound Attestation

Status: `BOOTSTRAP — RATIFY IN REAL REPOSITORY`

## Lease identity

A v1.2 lease is valid only at the repository root and records the clean committed base HEAD plus branch. Task and READY receipts must be committed before activation. A checkout, commit, rebase, branch switch, or task/review edit invalidates authority.

The worktree may become dirty after activation because implementation is the intended change. Only paths in `allowed_paths` may be changed through governed tools.

## Implementation seal

The human operator runs `python scripts/seal_implementation.py` after implementation. The script:

1. revalidates the active lease and repository identity;
2. enumerates tracked and untracked changes;
3. rejects any changed path outside the task lease;
4. hashes the binary Git diff plus each untracked file;
5. writes a local seal and changes the lease to `SEALED`.

Reviewers must recompute or independently inspect the seal. A seal is provenance evidence, not proof of correctness.

## R4 signed approval

R4 tasks require `approval_mode: ssh-signature`. The independent reviewer finalizes the READY receipt and signs it outside Claude:

```bash
ssh-keygen -Y sign -f /secure/path/reviewer_key -n aigdo-ready-review READY-REVIEW.md
```

Commit the `.sig` file and a public-key allowlist in a reviewed project path. The allowlist uses OpenSSH allowed-signers format:

```text
reviewer@example.com ssh-ed25519 AAAA...
```

Record both paths in the receipt. `activate_lease.py` verifies namespace, reviewer identity, signature, and trusted public key. Never store the private key in the repository.

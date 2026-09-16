# Governance control plane

This directory is controlled by deterministic scripts and hooks. Agents must not modify it.

`implementation-lease.json` is created only when a human runs `scripts/activate_lease.py` outside Claude. It is intentionally ignored by Git. The hook checks its expiry, task/review hashes, base Git HEAD, branch, approved paths, and approved commands on every relevant tool call.

`mcp-policy.json` is committed policy. MCP access is deny-by-default without a lease; exact tool names may be allowlisted after human review.

`implementation-seals/` is an ignored local archive populated only by the human-operated sealing script. Seal names bind task, task hash, and base commit so later tasks cannot silently overwrite earlier local provenance. Sealing freezes the exact diff digest and changes the lease state to `SEALED`, so further agent writes are denied.
